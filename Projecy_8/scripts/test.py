import pandas as pd
import pika

metall = [
    'aluminium', 'copper',
    'lead', 'nickel', 'zink'
]


def get_metalls(metall_name: str):

    # Cоздадим датафрейм из БД
    data = pd.read_csv(
        f'./data/{metall_name}.csv', index_col='date', parse_dates=['date'])

    return data


if __name__ == '__main__':
    # Создание подключения к RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Создание очереди для отправки сообщений
    channel.queue_declare(queue='raw_aluminium_queue')
    channel.queue_declare(queue='raw_copper_queue')
    channel.queue_declare(queue='raw_lead_queue')
    channel.queue_declare(queue='raw_nickel_queue')
    channel.queue_declare(queue='raw_zink_queue')

    for i in metall:
        # Получение данных
        data = get_metalls(i)

        # Отправка данных в очередь RabbitMQ
        channel.basic_publish(exchange='', routing_key=f'raw_{i}_queue', body=f'{data.to_json()}')

    # Закрытие подключения к RabbitMQ
    connection.close()
