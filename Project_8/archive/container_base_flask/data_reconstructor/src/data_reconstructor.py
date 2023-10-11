import numpy as np
import pandas as pd
import json
import pika

metall = [
    'aluminium', 'copper',
    'lead', 'nickel', 'zink'
]


def callback(ch, method, properties, body):
    # Ответ из очереди
    data_raw = json.loads(body)
    key_route = data_raw['id']
    data = json.loads(data_raw['body'])

    # Преобразование ответа
    data = pd.DataFrame(data)
    data.replace(0, np.nan, inplace=True)
    data.dropna(inplace=True, axis=0)
    data.reset_index(inplace=True)

    # Convert milliseconds to seconds
    data.iloc[:, 0] = pd.to_numeric(data.iloc[:, 0]) / 1000
    data.iloc[:, 0] = pd.to_datetime(
        data.iloc[:, 0], unit='s')  # Convert seconds to datetime

    data.set_index(data.columns.to_list()[0], inplace=True)

    data = data.resample('d').interpolate(method='linear')

    data.reset_index(inplace=True)

    data = data.rename(columns={data.columns.to_list()[0]: 'date'})

    # Подготовка таблицы для сдвига фючерсов
    data_prognosis = pd.DataFrame(columns=['date'])
    start_date = str(data['date'].iloc[-1] + pd.DateOffset(days=1))
    date_range = pd.date_range(start_date, periods=90, freq='D')
    data_prognosis['date'] = date_range

    # Объединение полученных таблиц
    data = pd.concat([data, data_prognosis])

    # Сортировка и восстановление индексов
    data = data.sort_values(by='date')

    # Произведем сдвиг LME stock 3-month, представляющим своего рода фьючерс на металл
    # (точнее представляет цену для операций сроком на 3 месяца.
    #  Это означает, что цена отражает стоимость металла на рынке с учетом сроковых контрактов на 3 месяца.)
    data.iloc[:, 2] = data.iloc[:, 2].shift(90)

    # Обрежем нижние nan-ы, т.к. мы получили наши фьючерсы
    data = data[~data.iloc[:, 2].isna()]

    data.set_index('date', inplace=True)

    # Отправим данные на модуль STOCK_AR
    channel.basic_publish(
        exchange='',
        routing_key=f'stock_ar_queue',
        body=json.dumps({
            'id': key_route,
            'body': data.to_json()}
        )
    )

    # Отправим данные на модуль SPOT_AR
    channel.basic_publish(
        exchange='',
        routing_key=f'spot_ar_queue',
        body=json.dumps({
            'id': key_route,
            'body': data.to_json()}
        )
    )



if __name__ == '__main__':
    # Создание подключения к RabbitMQ
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()

    # Создание очередей для принятия сообщений
    channel.queue_declare(queue=f'raw_queue')

    channel.queue_declare(queue=f'stock_ar_queue')

    channel.queue_declare(queue=f'spot_ar_queue')

    channel.basic_consume(
        queue=f'raw_queue',
        on_message_callback=callback,
        auto_ack=True
    )

    # Закрытие подключения к RabbitMQ
    print('...Ожидание сообщений, для выхода нажмите CTRL+C')
    channel.start_consuming()
