import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from IPython.display import display

import warnings
warnings.filterwarnings("ignore")


# Загрузка данных (в будущем этот и следующий шаг можно заменить на выгрузку sql)
def load_data():
    customers = pd.read_csv("./clean_data/customers.csv")
    geolocation = pd.read_csv("./clean_data/geolocation.csv")
    order_pay = pd.read_csv("./clean_data/order_payments.csv")
    reviews = pd.read_csv("./clean_data/order_reviews.csv")
    orders = pd.read_csv("./clean_data/orders.csv")
    item = pd.read_csv("./clean_data/orders_items.csv")
    category_name = pd.read_csv(
        "./clean_data/product_category_name_translation.csv")
    products = pd.read_csv("./clean_data/products.csv")
    sellers = pd.read_csv("./clean_data/sellers.csv")
    return customers, geolocation, order_pay, reviews, orders, item, category_name, products, sellers


# Объединение данных
def merge_data(orders, item, order_pay, reviews, products, customers, sellers, category_name):
    df = orders.merge(item, on='order_id', how='left')
    df = df.merge(order_pay, on='order_id', how='outer', validate='m:m')
    df = df.merge(reviews, on='order_id', how='outer')
    df = df.merge(products, on='product_id', how='outer')
    df = df.merge(customers, on='customer_id', how='outer')
    df = df.merge(sellers, on='seller_id', how='outer')
    df = df.merge(category_name, on="product_category_name", how="left")
    return df

# Очистка данных: удаление строк без customer_unique_id


def filter_customers(df):
    return df[~df["customer_unique_id"].isna()]


def calculate_rfm(df):
    """Расчет RFM-метрик с обработкой исключений"""
    try:
        df['order_purchase_timestamp'] = pd.to_datetime(
            df['order_purchase_timestamp'])
        current_date = df['order_purchase_timestamp'].max()

        return df.groupby('customer_unique_id').agg(
            Recency=(
                'order_purchase_timestamp',
                lambda x: (current_date - x.max()).days),
            Frequency=('order_id', 'nunique'),
            Monetary=('product_id', 'count')
        ).reset_index()
    except KeyError as e:
        print(f"Ошибка: Отсутствует необходимая колонка {e}")
        return pd.DataFrame()


def add_rfm_segments(rfm_data):
    """Добавление RFM-сегментов с весами"""
    quantiles = rfm_data[['Recency', 'Frequency', 'Monetary']].quantile(
        [0.25, 0.5, 0.75]).to_dict()

    def rank_rfm(x, metric):
        """
        Параметры:
        x : float - значение метрики (Recency, Frequency, Monetary) для клиента
        metric : str - название метрики ('Recency', 'Frequency', 'Monetary')
        quantiles : dict - словарь с квартилями для всех метрик

        Возвращает:
        int - ранг от 1 до 4, где для Recency 4 - лучший, для Frequency/Monetary 4 - худший

        Примечание: 
        Для Recency используется обратная шкала (меньше дней = лучше)
        Для Frequency и Monetary - прямая шкала (больше значений = лучше)
        Квартили рассчитываются для всей популяции клиентов

        """

        # Логика ранжирования для Recency
        if metric == 'Recency':
            # Чем меньше дней прошло с последней покупки (ниже Recency), тем лучше
            if x <= quantiles[metric][0.25]:
                return 4  # Топ-25% самых активных (покупали недавно)
            elif x <= quantiles[metric][0.5]:
                return 3  # 25-50% - выше среднего
            elif x <= quantiles[metric][0.75]:
                return 2  # 50-75% - ниже среднего
            else:
                return 1  # Худшие 25% - давно не покупали

        # Логика ранжирования для Frequency и Monetary
        else:
            # Чем больше покупок/сумма (выше значения), тем лучше
            if x <= quantiles[metric][0.25]:
                return 1  # Худшие 25% - редко/мало покупают
            elif x <= quantiles[metric][0.5]:
                return 2  # 25-50% - ниже среднего
            elif x <= quantiles[metric][0.75]:
                return 3  # 50-75% - выше среднего
            else:
                return 4  # Топ-25% - самые частые/крупные покупатели

    for metric in ['Recency', 'Frequency', 'Monetary']:
        rfm_data[f'{metric[0]}_rank'] = rfm_data[metric].apply(
            rank_rfm, metric=metric)

    # Взвешенная оценка
    weights = {'R': 0.5, 'F': 0.3, 'M': 0.2}
    rfm_data['RFM_Weighted'] = sum(
        rfm_data[f'{k}_rank']*v for k, v in weights.items())

    # Автоматическая классификация
    rfm_data['Churn_Risk'] = pd.qcut(
        rfm_data['RFM_Weighted'],
        q=[0, 0.25, 0.75, 1],
        labels=['3_high', '2_medium', '1_low']  # Формат для сортировки
    )
    return rfm_data


def save_churn_plot(rfm_data, filename='plots/churn_risk_distribution.png'):
    """Сохранение графика распределения рисков оттока"""
    try:
        # Создаем директорию если нужно
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        plt.figure(figsize=(12, 6))
        ax = sns.countplot(
            x='Churn_Risk',
            data=rfm_data,
            order=['Высокий риск', 'Средний риск', 'Низкий риск'],
            palette={'Высокий риск': 'red',
                     'Средний риск': 'orange', 'Низкий риск': 'green'}
        )

        # Добавляем аннотации
        for p in ax.patches:
            ax.annotate(f'{p.get_height():.0f}',
                        (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center',
                        va='center',
                        xytext=(0, 5),
                        textcoords='offset points')

        plt.title('Распределение клиентов по риску оттока')
        plt.xlabel('Категория риска')
        plt.ylabel('Количество клиентов')
        plt.xticks(rotation=45)

        # Сохраняем и закрываем график
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f'График сохранен в {filename}')

    except Exception as e:
        print(f'Ошибка при сохранении графика: {str(e)}')

def save_labels(label_data, filename='labels/labels.csv'):
    try:
        # Создаем директорию если нужно
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        label_data.to_csv(filename, index=False)
        
    except Exception as e:
        print(f'Ошибка при сохранении лэйблов: {str(e)}')
    pass

def main_pipeline():
    """Главный конвейер обработки данных"""
    # Шаг 1: Загрузка данных
    customers, geolocation, order_pay, reviews, orders, item, category_name, products, sellers = load_data()

    # Шаг 2: Объединение данных
    df = merge_data(orders, item, order_pay, reviews, products,
                    customers, sellers, category_name)

    # Шаг 3: Фильтрация пропусков
    data = filter_customers(df)

    # Шаг 4: Расчет rfm
    rfm_raw = calculate_rfm(data)

    # Шаг 5: Объединение данных
    rfm_segment = add_rfm_segments(rfm_raw)
    
    # Шаг 6: Сохраняем график для дашборда
    save_churn_plot(rfm_segment, 'results/plots/churn_distribution.png')
    
    # Шаг 7: Вычленяем лэйблы для классификации
    label_data = rfm_segment.copy()[['customer_unique_id', 'Churn_Risk']]
    risk_mapping = {'3_high': 3, '2_medium': 2, '1_low': 1}
    label_data['Churn_Risk'] = label_data['Churn_Risk'].map(risk_mapping)
    
    # Шаг 8: Сохранение лэйблов для обучения классификатора
    save_labels(label_data,'results/labels/labels.csv')

    return rfm_segment, label_data


# Запуск пайплайна и вывод результатов
if __name__ == "__main__":
    rfm_result, label_data  = main_pipeline()

    print("\nПример данных:")
    display(rfm_result.head(3))

    print("\nРаспределение классов:")
    print(label_data['Churn_Risk'].value_counts(normalize=True).sort_index())

    print("\nПервые 5 записей для классификатора:")
    display(label_data.head())