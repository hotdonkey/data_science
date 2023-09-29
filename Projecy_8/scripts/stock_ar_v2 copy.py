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

def working_data_getter(data_raw, element):
    if data_raw['id'] == f'{element}' and data_raw['type'] == 'working_data':

        working_data = pd.DataFrame(json.loads(data_raw['body']))
        # Standart reconstruction
        working_data.reset_index(inplace=True)

        # Convert milliseconds to seconds
        working_data.iloc[:, 0] = pd.to_numeric(
            working_data.iloc[:, 0]) / 1000

        working_data.iloc[:, 0] = pd.to_datetime(
            working_data.iloc[:, 0], unit='s')  # Convert seconds to datetime

        working_data.set_index(
            working_data.columns.to_list()[0], inplace=True)

        working_data.index.freq = 'D'

        ar_model_real_stock = AutoReg(
            working_data.iloc[:, -1], lags=1, seasonal=True).fit()

        pred_real_stock = ar_model_real_stock.predict(
            start=len(working_data), end=len(working_data)+89)

        return pred_real_stock
    else:
        return None


def target_data_getter(data_raw, element):
    if data_raw['id'] == f'{element}' and data_raw['type'] == 'target_data':
        target_data = pd.DataFrame(json.loads(data_raw['body']))

        # Standart reconstruction
        target_data.reset_index(inplace=True)

        # Convert milliseconds to seconds
        target_data.iloc[:, 0] = pd.to_numeric(
            target_data.iloc[:, 0]) / 1000

        target_data.iloc[:, 0] = pd.to_datetime(
            target_data.iloc[:, 0], unit='s')  # Convert seconds to datetime

        target_data.set_index(
            target_data.columns.to_list()[0], inplace=True)

        target_data.index.freq = 'D'

        return target_data


def callback1(ch, method, properties, body):
    data_raw = json.loads(body)
    pass
    
    
def callback2(ch, method, properties, body):
    data_raw = json.loads(body)    
    
    pass

def callback3(ch, method, properties, body):
    data_raw = json.loads(body) 
    
    pass      
        
if __name__ == '__main__':
    # Создание подключения к RabbitMQs
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Создание очередей для получения сообщений
    channel.queue_declare(queue=f'stock_ar_working_queue')
    channel.queue_declare(queue=f'stock_ar_target_queue')
    channel.queue_declare(queue=f'stock_ar_garch_queue')

    channel.basic_consume(
        queue=f'stock_ar_working_queue',
        on_message_callback=callback1,
        auto_ack=True
    )
    
    channel.basic_consume(
        queue=f'stock_ar_target_queue',
        on_message_callback=callback2,
        auto_ack=True
    )
    
    channel.basic_consume(
        queue=f'stock_ar_garch_queue',
        on_message_callback=callback3,
        auto_ack=True
    )

    print('...Ожидание сообщений, для выхода нажмите CTRL+C')
    channel.start_consuming()

'''def callback(ch, method, properties, body):
    data_raw = json.loads(body)
    
    if 'id' in data_raw and 'type' in data_raw:
        key_route = data_raw['id']
        df_type = data_raw['type']
        data = json.loads(data_raw['body'])

        data = pd.DataFrame(data)

        working_data = pd.DataFrame()
        target_data = pd.DataFrame()
        garch_data = pd.DataFrame()
        pred_real_stock = pd.DataFrame()

        for element in metall:
            working_data = working_data_getter(element)
            print(working_data)

        for element in metall:
            
            if data_raw['id'] == f'{element}' and data_raw['type'] == 'working_data':
                working_data = pd.DataFrame(json.loads(data_raw['body']))
                # Standart reconstruction
                working_data.reset_index(inplace=True)

                # Convert milliseconds to seconds
                working_data.iloc[:, 0] = pd.to_numeric(
                    working_data.iloc[:, 0]) / 1000
                
                working_data.iloc[:, 0] = pd.to_datetime(
                    working_data.iloc[:, 0], unit='s')  # Convert seconds to datetime
                
                working_data.set_index(
                    working_data.columns.to_list()[0], inplace=True)
                
                working_data.index.freq = 'D'

                ar_model_real_stock = AutoReg(
                    working_data.iloc[:, -1], lags=1, seasonal=True).fit()

                pred_real_stock = ar_model_real_stock.predict(
                    start=len(working_data), end=len(working_data)+89)
                
                print(pred_real_stock)

            elif data_raw['id'] == f'{element}' and data_raw['type'] == 'target_data':
                target_data = pd.DataFrame(json.loads(data_raw['body']))
                
                # Standart reconstruction
                target_data.reset_index(inplace=True)

                # Convert milliseconds to seconds
                target_data.iloc[:, 0] = pd.to_numeric(
                    target_data.iloc[:, 0]) / 1000
                
                target_data.iloc[:, 0] = pd.to_datetime(
                    target_data.iloc[:, 0], unit='s')  # Convert seconds to datetime
                
                target_data.set_index(
                    target_data.columns.to_list()[0], inplace=True)
                
                target_data.index.freq = 'D'
                
                print(target_data.iloc[:,-1])
            
                
            elif data_raw['id'] == f'{element}' and data_raw['type'] == 'garch':
                garch_data = pd.DataFrame(json.loads(data_raw['body']))
                garch_data.reset_index(inplace=True)
                
                garch_data['index'] = pd.to_numeric(garch_data['index'])
                garch_data = garch_data.sort_values('index')
                
                garch_data.set_index('index', inplace=True)
                
                #print(garch_data)


if __name__ == '__main__':
    # Создание подключения к RabbitMQs
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Создание очередей для получения сообщений

    channel.queue_declare(queue=f'stock_ar_queue')

    channel.basic_consume(
        queue=f'stock_ar_queue',
        on_message_callback=callback,
        auto_ack=True
    )

    print('...Ожидание сообщений, для выхода нажмите CTRL+C')
    channel.start_consuming()
'''