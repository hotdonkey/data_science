import numpy as np
import pandas as pd
import json
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
    
    data = pd.DataFrame(data)

    print(method.routing_key)


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
            on_message_callback=callback,
            auto_ack=True
        )

    for key in metall:
        channel.basic_consume(
            queue=f'stock_ar_{key}_reconstr_w_queue',
            on_message_callback=callback,
            auto_ack=True
        )
    
    for key in metall:
        channel.basic_consume(
            queue=f'stock_ar_{key}_reconstr_t_queue',
            on_message_callback=callback,
            auto_ack=True
        )

    print('...Ожидание сообщений, для выхода нажмите CTRL+C')
    channel.start_consuming()
