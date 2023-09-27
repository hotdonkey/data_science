import numpy as np
import pandas as pd
import json
import pickle
import pika

metall = [
    'aluminium', 'copper',
    'lead', 'nickel', 'zink'
]

def callback(ch, method, properties, body):
    data = json.loads(body)
    data = pd.DataFrame(data)
    
    data.reset_index(inplace=True)
    
    # Convert milliseconds to seconds
    data.iloc[:, 0] = pd.to_numeric(data.iloc[:, 0]) / 1000
    data.iloc[:, 0] = pd.to_datetime(
        data.iloc[:, 0], unit='s')  # Convert seconds to datetime

    data.set_index(data.columns.to_list()[0], inplace=True)
    
    print(data)


if __name__ == '__main__':
    # Создание подключения к RabbitMQ
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='garch_queue')

    channel.basic_consume(
        queue=f'garch_queue',
        on_message_callback=callback,
        auto_ack=True
    )
    
    print('...Ожидание сообщений, для выхода нажмите CTRL+C')
    channel.start_consuming()