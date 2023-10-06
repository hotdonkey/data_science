import numpy as np
import pandas as pd
import json
import pickle
import pika


metall_dict = {
    'aluminium': 'al', 'copper': 'cu',
    'lead': 'pb', 'nickel': 'nk', 'zink': 'zn'
}


def callback(ch, method, properties, body):
    data_raw = json.loads(body)

    key = data_raw['id']

    data = pd.DataFrame(json.loads(data_raw['body']))

    split_param = (data.iloc[:, 0].isna())  # & (data.iloc[:, 2].isna())

    data_target = data[split_param]

    working_data = data[~split_param]

    data.reset_index(inplace=True)

    data.rename(columns={'index': 'date'}, inplace=True)

    # Теперь поделим рабочую выборку
    train_dt = working_data.iloc[:-90]
    test_dt = working_data.iloc[-90:]

    # Выделим выборки для обучения
    X_train = train_dt.drop(data.columns.to_list()[1], axis=1)
    y_train = train_dt[data.columns.to_list()[1]]

    X_test = test_dt.drop(data.columns.to_list()[1], axis=1)

    # Распиклим модель с оптимальными параметрами
    # просто что бы показать что умею солить модели
    with open(f'./models/decision_tree_{metall_dict[key]}.pkl', 'rb') as pkl_file:
        dt_pkl_model = pickle.load(pkl_file)

    # Произведем моделирование
    dt_pkl_model.fit(X_train, y_train)

    pred_dt_final = dt_pkl_model.predict(X_test)

    pred_dt_final = np.array(pred_dt_final).reshape(-1, 1)

    data_target.iloc[:, 0] = pred_dt_final

    data_target.reset_index(inplace=True)

    # Convert milliseconds to seconds
    data_target.iloc[:, 0] = pd.to_numeric(data_target.iloc[:, 0]) / 1000
    data_target.iloc[:, 0] = pd.to_datetime(
        data_target.iloc[:, 0], unit='s')  # Convert seconds to datetime
    data_target.set_index(data_target.columns.to_list()[0], inplace=True)

    data_target.index.freq = 'D'

    working_data.reset_index(inplace=True)

    # Convert milliseconds to seconds
    working_data.iloc[:, 0] = pd.to_numeric(working_data.iloc[:, 0]) / 1000
    working_data.iloc[:, 0] = pd.to_datetime(
        working_data.iloc[:, 0], unit='s')  # Convert seconds to datetime
    working_data.set_index(working_data.columns.to_list()[0], inplace=True)

    working_data.index.freq = 'D'

    result_data = pd.concat([working_data, data_target])

    # Сохранение результата прогноза авторегрессии
    result_data.to_csv(
        f'./results/intermediate/spot_dt_prognosis_{key}.csv', sep=',')

    # Сохранение результата для формирования обобщенного прогноза
    data_target.to_csv(
        f'./results/intermediate/spot_dt_result_{key}.csv', sep=',')

    print(key, result_data)


if __name__ == '__main__':
    # Создание подключения к RabbitMQ
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Создание очередей для получения сообщений
    channel.queue_declare(queue=f'spot_dt_queue')

    # Создание очередей для отправки сообщений
    channel.queue_declare(queue=f'prognosis_dt_queue')

    # Получение запроса
    channel.basic_consume(
        queue=f'spot_dt_queue',
        on_message_callback=callback,
        auto_ack=True
    )

    print('...Ожидание сообщений, для выхода нажмите CTRL+C')
    channel.start_consuming()
