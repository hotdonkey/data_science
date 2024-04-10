import numpy as np
import pandas as pd
from lightfm import LightFM
from lightfm.evaluation import precision_at_k
from scipy.sparse import coo_matrix
from sklearn.preprocessing import LabelEncoder

# Получение данных для коллаборативной фильтрации
events_raw = pd.read_csv("./data/events.csv")


# Основная функция рекомендаций
def rs_batch(data, lb_interactions, upb_ineractions, top_items, month_border=7):
    events = data.copy()

    # Приведем к временному формату данные из timestapm
    events["timestamp"] = pd.to_datetime(events["timestamp"], unit="ms")
    events.rename(columns={"timestamp": "date"}, inplace=True)
    events["date"] = pd.to_datetime(events["date"].dt.date)
    events = events.sort_values("date").reset_index(drop=True)
    events = events[["visitorid", "itemid", "event", "date"]]

    # Фильтруем по количеству больше указываемой отметки и оставляем только itemid и count
    item_border = top_items

    top_items = pd.DataFrame(
        events.groupby("itemid")["event"].value_counts()
    ).reset_index()
    top_items = top_items[top_items["count"] >= item_border][["itemid", "count"]]
    top_items = top_items.groupby("itemid")["count"].sum().to_dict()

    # Создаем новый столбец num_occur, в котором хранится количество событий для каждого itemid
    # сюда входят просмотры, добавления и покупки
    events["num_occur"] = events["itemid"].map(top_items)

    # Фильтруем события, оставляем только те, у которых num_occur находится в заданом интервале
    lower_border = lb_interactions
    upper_border = upb_ineractions

    events_processed = events[
        (events["num_occur"] >= lower_border) & (events["num_occur"] < upper_border)
    ]
    events_processed = events_processed.drop(columns="num_occur")
    events_processed = events_processed.drop_duplicates().reset_index(drop=True)

    # Выделяем обучающий набор данных до указаной отметки
    events_train = events_processed[events_processed["date"].dt.month < month_border]
    # Выделяем тестовый набор данных после указаной отметки
    events_test = events_processed[events_processed["date"].dt.month >= month_border]

    # Фильтруем тестовый набор данных
    events_test = events_test[
        (events_test["visitorid"].isin(events_train["visitorid"]))
        & (events_test["itemid"].isin(events_train["itemid"]))
    ]

    # Список категориальных признаков
    id_cols = ["visitorid", "itemid"]

    # Создаем словарь для закодированных значений обучающего набора
    trans_cat_train = dict()
    # Создаем словарь для закодированных значений тестового набора
    trans_cat_test = dict()

    # Применяем кодирование юзеров и айтемов
    for k in id_cols:
        cate_enc = LabelEncoder()
        trans_cat_train[k] = cate_enc.fit_transform(
            events_train[k].values
        )  # Кодируем значения обучающего набора
        trans_cat_test[k] = cate_enc.transform(
            events_test[k].values
        )  # Кодируем значения тестового набора

    # Создаем словарь для закодированных значений целевой переменной
    ratings = dict()

    cate_enc_2 = LabelEncoder()
    ratings["train"] = cate_enc_2.fit_transform(
        events_train.event
    )  # Кодируем целевую переменную для обучающего набора
    ratings["test"] = cate_enc_2.transform(
        events_test.event
    )  # Кодируем целевую переменную для тестового набора

    # Вычисляем количество уникальных пользователей
    n_users = len(np.unique(trans_cat_train["visitorid"]))
    # Вычисляем количество уникальных товаров
    n_items = len(np.unique(trans_cat_train["itemid"]))

    # Создаем словарь для матриц оценок
    rate_matrix = dict()

    # Создаем разреженную матрицу для обучающего набора
    rate_matrix["train"] = coo_matrix(
        (ratings["train"], (trans_cat_train["visitorid"], trans_cat_train["itemid"])),
        shape=(n_users, n_items),
    )
    # Создаем разреженную матрицу для тестового набора
    rate_matrix["test"] = coo_matrix(
        (
            ratings["test"],  # данные
            (trans_cat_test["visitorid"], trans_cat_test["itemid"]),
        ),  # индексы строк (trans_cat_test[“visitorid”]) и индексы столбцов (trans_cat_test[“itemid”])
        shape=(n_users, n_items),
    )

    # Создаем модель LightFM с указанием параметров
    model = LightFM(no_components=50, loss="warp")
    # Обучаем модель на обучающей матрице
    model.fit(rate_matrix["train"], epochs=100, num_threads=8)

    # Вычисляем среднюю точность на тестовой матрице для k=5
    map_at3 = precision_at_k(model, rate_matrix["test"], k=5).mean()
    print(f"For batch {lb_interactions}-{upb_ineractions} interactions")
    print(f"Mean Average Precision at 5: {round(map_at3*100, 3)} %.")

    # Используем обученную модель для предсказания предпочтений пользователей для товаров в тестовой выборке
    predicted_scores = model.predict(
        trans_cat_test["visitorid"], trans_cat_test["itemid"], num_threads=8
    )

    # Создаем функцию для получения предсказанных оценок для всех возможных пар (пользователь, товар) в тестовой выборке
    def get_predicted_ratings(visitor_ids, item_ids, scores):
        predicted_ratings = pd.DataFrame(
            {"visitorid": visitor_ids, "itemid": item_ids, "predicted_score": scores}
        )
        return predicted_ratings

    # Преобразуем полученные предсказанные оценки в датафрейм с колонками visitorid и itemid
    predicted_ratings_df = get_predicted_ratings(
        events_test["visitorid"], events_test["itemid"], predicted_scores
    )

    # Берем только отрицательные значения ибо они то нам и нужны
    predicted_ratings_df = predicted_ratings_df[
        predicted_ratings_df["predicted_score"] < 0
    ]

    # Создаем сводную содержащую скоры ны пересечении айтемов и юзеров
    predicted_ratings_pivot = pd.pivot_table(
        data=predicted_ratings_df,
        index="visitorid",
        columns="itemid",
        values="predicted_score",
        aggfunc="sum",
    )

    # Вытащим внутрености сводной
    users = predicted_ratings_pivot.index.to_list()
    items = predicted_ratings_pivot.columns.to_list()
    scores = np.array(predicted_ratings_pivot)

    # Начинаем вытаскивать предикты ибо lightfm возвращает индексы
    rec_list = []

    # Проходимся циклом по юзерам
    for i in range(len(users)):
        var_list = []
        # Ищем 3 максимальных индекса
        best_var = np.argsort(scores[i])[:5].tolist()

        # Бежим по индексам и вытаскиваем айтемы
        for j in best_var:
            var_list.append(items[j])

        rec_list.append(var_list)

    # Заворачиваем в датафрейм
    recommendations = pd.DataFrame(data={"users": users, "recommendations": rec_list})

    return recommendations


def rs_system(data_rs):

    # Формируем 3 основные группы пользователей
    # Рандомов с ниским количеством интеракций
    random_customers = rs_batch(
        data=data_rs, lb_interactions=0, upb_ineractions=500, top_items=40
    )

    # Посльзователей из средней группы
    temp_customers = rs_batch(
        data=data_rs, lb_interactions=500, upb_ineractions=1000, top_items=10
    )

    # И самых выжных
    mvp_customers = rs_batch(
        data=data_rs, lb_interactions=1000, upb_ineractions=100000, top_items=10
    )

    # Почистим дублирующие рекомендации для юзеров с приоритетом MVP->Temp->Random
    temp_customers = temp_customers[
        ~temp_customers["users"].isin(mvp_customers["users"])
    ]

    random_customers = random_customers[
        ~random_customers["users"].isin(mvp_customers["users"])
    ]
    random_customers = random_customers[
        ~random_customers["users"].isin(temp_customers["users"])
    ]

    print(f"Random_customer_batch size = {random_customers.shape[0]}")
    print(f"Temp_customer_batch size = {temp_customers.shape[0]}")
    print(f"MVP_customer_batch size = {mvp_customers.shape[0]}")

    recomendation_df = pd.concat(
        [random_customers, temp_customers, mvp_customers]
    ).reset_index(drop=True)

    return recomendation_df


# Дефолтная рекомендация
def default_recommendation(data_raw, data_rec):
    # Получим топ-3 товара
    data = data_raw.copy()

    top_3_items = (
        data[data["event"] == "transaction"]["itemid"]
        .value_counts()[:5]
        .index.to_list()
    )
    top_3_items

    # Вытащим всех уникальных пользователей
    unique_usrs = set(data["visitorid"])

    # Юзеры для которых были сгенерированы рекомендации
    recommended_users = set(data_rec["users"])

    default_usr = list(unique_usrs - recommended_users)
    default_rec = pd.DataFrame(data={"users": default_usr, "recommendations": 0})
    default_rec["recommendations"] = default_rec["recommendations"].apply(
        lambda x: top_3_items
    )

    return default_rec


# Скрипт запуска
def run_rs_system_script():
    try:
        recommendation_df = rs_system(events_raw)
        default_rec_df = default_recommendation(events_raw, recommendation_df)
        final_df = pd.concat([recommendation_df, default_rec_df]).reset_index(drop=True)
        recommendation_df.to_csv("./data/rs_backup.csv", index=0)
        final_df.to_csv("./data/final_backup.csv", index=0)

    except KeyError:
        print("Проверьте источник данных на соответствие структуре")
    except ValueError:
        print("Вероятное превышение границы временного интервала в rs_batch")


if __name__ == "__main__":
    run_rs_system_script()
