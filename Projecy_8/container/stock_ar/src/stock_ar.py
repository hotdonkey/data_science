import numpy as np
import pandas as pd
import json
from statsmodels.tsa.ar_model import AutoReg
import pickle
import pika


metall_dict = {
    'aluminium': 'al', 'copper': 'cu',
    'lead': 'pb', 'nickel': 'nk', 'zink': 'zn'
}


def callback(ch, method, properties, body):
    data_raw = json.loads(body)

    key = data_raw['id']

    with open(f'./models/ar_stock_{metall_dict[key]}.pkl', 'rb') as pkl_file:
        stock_params = pickle.load(pkl_file)

    lags = stock_params['order'][0]

    data = pd.DataFrame(json.loads(data_raw['body']))

    data.reset_index(inplace=True)

    # Convert milliseconds to seconds
    data.iloc[:, 0] = pd.to_numeric(data.iloc[:, 0]) / 1000
    data.iloc[:, 0] = pd.to_datetime(
        data.iloc[:, 0], unit='s')  # Convert seconds to datetime
    data.set_index(data.columns.to_list()[0], inplace=True)

    data.index.freq = 'D'

    split_param = (data.iloc[:, 0].isna()) & (data.iloc[:, 2].isna())

    data_target = data[split_param]

    working_data = data[~split_param]

    ar_model_real_stock = AutoReg(
        working_data.iloc[:, -1], lags=lags, seasonal=True).fit()

    pred_real_stock = ar_model_real_stock.predict(
        start=len(working_data), end=len(working_data)+89)

    data_target.iloc[:, 2] = pred_real_stock

    result_data = pd.concat([working_data, data_target])

    channel.basic_publish(
        exchange='',
        routing_key=f'spot_dt_queue',
        body=json.dumps({
            'id': key,
            'body': result_data.to_json()}
        )
    )

    print(key, result_data)


if __name__ == '__main__':
    # Создание подключения к RabbitMQ
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()

    # Создание очередей для получения сообщений

    channel.queue_declare(queue=f'stock_ar_queue')

    # Создание очередей для отправки сообщений
    channel.queue_declare(queue=f'spot_dt_queue')

    # Получение запроса
    channel.basic_consume(
        queue=f'stock_ar_queue',
        on_message_callback=callback,
        auto_ack=True
    )

    print('...Ожидание сообщений, для выхода нажмите CTRL+C')
    channel.start_consuming()
