import numpy as np
import pandas as pd
from datetime import datetime
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

    # Разделим датасет на две выборки:
    # рабочую информацию (для трейн/тест) и часть
    # для будущего прогноза неизвестного периода
    split_param = (data.iloc[:, 0].isna()) & (data.iloc[:, 2].isna())

    # on: Spot_AR/ Stock_AR
    data_target = data[split_param]
    # on: Garch/ Spot_AR/ Stock_AR/ Spot_DT/ Prognosis
    working_data = data[~split_param]

    # Отправим данные на модуль GARCH
    channel.basic_publish(
        exchange='',
        routing_key=f'garch_{key_route}_queue',
        body=json.dumps({
            'id': key_route,
            'body': working_data.to_json()}
        )
    )
    
    # Отправим данные на модуль STOCK_AR
    channel.basic_publish(
        exchange='',
        routing_key=f'stock_ar_{key_route}_reconstr_w_queue',
        body=json.dumps({
            'id': key_route,
            'body': working_data.to_json()}
        )
    )
    
    channel.basic_publish(
        exchange='',
        routing_key=f'stock_ar_{key_route}_reconstr_t_queue',
        body=json.dumps({
            'id': key_route,
            'body': data_target.to_json()}
        )
    )

    # Теперь поделим рабочую выборку
    # train = working_data.iloc[:-90]
    # test = working_data.iloc[-90:]

    print(f'Answer: {key_route, data}')


if __name__ == '__main__':
    # Создание подключения к RabbitMQ
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Создание очередей для принятия сообщений
    for i in metall:
        channel.queue_declare(queue=f'raw_{i}_queue')

    # Создание очередей для отправки сообщений
    for i in metall:
        channel.queue_declare(queue=f'garch_{i}_queue')

    for i in metall:
        channel.queue_declare(queue=f'spot_ar_{i}_reconstr_w_queue')
        
    for i in metall:
        channel.queue_declare(queue=f'spot_ar_{i}_reconstr_t_queue')

    for i in metall:
        channel.queue_declare(queue=f'stock_ar_{i}_reconstr_w_queue')
        
    for i in metall:
        channel.queue_declare(queue=f'stock_ar_{i}_reconstr_t_queue')

    for i in metall:
        channel.queue_declare(queue=f'spot_dt_{i}_reconstr_queue')

    for i in metall:
        channel.queue_declare(queue=f'prognosis_{i}_reconstr_queue')

    for i in metall:
        # Получение данных
        channel.basic_consume(
            queue=f'raw_{i}_queue',
            on_message_callback=callback,
            auto_ack=True
        )

    # Закрытие подключения к RabbitMQ
    print('...Ожидание сообщений, для выхода нажмите CTRL+C')
    channel.start_consuming()
