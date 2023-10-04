import pandas as pd
import json
import pika

metall = [
    'aluminium', 'copper',
    'lead', 'nickel', 'zink'
]


def get_metalls(metall_name: str, channel):
    # Create a dataframe from the database
    data = pd.read_csv(
        f'./data/{metall_name}.csv', index_col='date', parse_dates=['date'])

    # Send data to the RabbitMQ queue
    channel.basic_publish(
        exchange='',
        routing_key='raw_queue',
        body=json.dumps({
            'id': metall_name,
            'type': 'raw_data',
            'body': data.to_json()
        })
    )

# Create a connection to RabbitMQ
connection = pika.BlockingConnection(
    pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()

# Declare the queue for sending messages
channel.queue_declare(queue='raw_queue')

for target in metall:
    get_metalls(target, channel)

# Close the connection to RabbitMQ
connection.close()
