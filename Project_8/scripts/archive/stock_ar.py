import numpy as np
import pandas as pd
import json
from statsmodels.tsa.ar_model import AutoReg
import pickle
import pika

metall = [
    'aluminium', 'copper',
    'lead', 'nickel', 'zink'
]

metall_dict = {
    'aluminium': 'al', 'copper': 'cu',
    'lead': 'pb', 'nickel': 'nk', 'zink': 'zn'
}


def callback(ch, method, properties, body):
    data_raw = json.loads(body)
    key_route = data_raw['id']
    data = json.loads(data_raw['body'])
    
    queue_name = method.routing_key
    queue_name = queue_name.split('_')
    queue_name = queue_name[-2:]
    queue_name = '_'.join(queue_name)
    
    
    
    
    
    print(queue_name)


if __name__ == '__main__':
    # Создание подключения к RabbitMQs
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Создание очередей для получения сообщений

    for i in metall:
        channel.queue_declare(queue=f'stock_ar_{i}_garch_queue')

    for i in metall:
        channel.queue_declare(queue=f'stock_ar_{i}_reconstr_w_queue')

    for i in metall:
        channel.queue_declare(queue=f'stock_ar_{i}_reconstr_t_queue')
    
    
    for key in metall:
        channel.basic_consume(
            queue=f'stock_ar_{key}_garch_queue',
            on_message_callback=callback,
            auto_ack=True
        )

        channel.basic_consume(
            queue=f'stock_ar_{key}_reconstr_w_queue',
            on_message_callback=callback,
            auto_ack=True
        )

        channel.basic_consume(
            queue=f'stock_ar_{key}_reconstr_t_queue',
            on_message_callback=callback,
            auto_ack=True
        ) 
        
    print('...Ожидание сообщений, для выхода нажмите CTRL+C')
    channel.start_consuming()

'''garch_result = {}
reconstr_w_result = {}
reconstr_t_result = {}


def callback_garch(ch, method, properties, body):
    data_raw = json.loads(body)
    key_route = data_raw['id']
    data = json.loads(data_raw['body'])

    # Standart reconstruction
    data = pd.Series(data)
    
    
    
    garch_result[key_route] = data
    print(garch_result)


def callback_reconstr_w(ch, method, properties, body):
    data_raw = json.loads(body)
    key_route = data_raw['id']
    data = json.loads(data_raw['body'])

    # Standart reconstruction
    data = pd.DataFrame(data)
    data.reset_index(inplace=True)

    # Convert milliseconds to seconds
    data.iloc[:, 0] = pd.to_numeric(data.iloc[:, 0]) / 1000
    data.iloc[:, 0] = pd.to_datetime(
        data.iloc[:, 0], unit='s')  # Convert seconds to datetime
    data.set_index(data.columns.to_list()[0], inplace=True)

    ar_model_real_stock = AutoReg(
        data.iloc[:, -1], lags=1, seasonal=True).fit()
    pred_real_stock = ar_model_real_stock.predict(
        start=len(data), end=len(data)+89)

    reconstr_w_result[key_route] = pred_real_stock
    #print(reconstr_w_result)
    


def callback_reconstr_t(ch, method, properties, body):
    data_raw = json.loads(body)
    key_route = data_raw['id']
    data = json.loads(data_raw['body'])

    # Standart reconstruction
    data = pd.DataFrame(data)
    data.reset_index(inplace=True)

    # Convert milliseconds to seconds
    data.iloc[:, 0] = pd.to_numeric(data.iloc[:, 0]) / 1000
    data.iloc[:, 0] = pd.to_datetime(
        data.iloc[:, 0], unit='s')  # Convert seconds to datetime
    data.set_index(data.columns.to_list()[0], inplace=True)
    
    reconstr_t_result[key_route] = data
    #print(reconstr_t_result)
    


if __name__ == '__main__':
    # Создание подключения к RabbitMQs
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Создание очередей для получения сообщений

    for i in metall:
        channel.queue_declare(queue=f'stock_ar_{i}_garch_queue')

    for i in metall:
        channel.queue_declare(queue=f'stock_ar_{i}_reconstr_w_queue')

    for i in metall:
        channel.queue_declare(queue=f'stock_ar_{i}_reconstr_t_queue')

    # Создание очередей для отправки сообщений

    for key in metall:
        channel.basic_consume(
            queue=f'stock_ar_{key}_garch_queue',
            on_message_callback=callback_garch,
            auto_ack=True
        )

        channel.basic_consume(
            queue=f'stock_ar_{key}_reconstr_w_queue',
            on_message_callback=callback_reconstr_w,
            auto_ack=True
        )

        channel.basic_consume(
            queue=f'stock_ar_{key}_reconstr_t_queue',
            on_message_callback=callback_reconstr_t,
            auto_ack=True
        )
        
        '''

