import numpy as np
import pandas as pd
import json
from arch import arch_model
from arch.__future__ import reindexing
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

    # Standart reconstruction
    data = pd.DataFrame(data)
    data.reset_index(inplace=True)

    # Convert milliseconds to seconds
    data.iloc[:, 0] = pd.to_numeric(data.iloc[:, 0]) / 1000
    data.iloc[:, 0] = pd.to_datetime(
        data.iloc[:, 0], unit='s')  # Convert seconds to datetime
    data.set_index(data.columns.to_list()[0], inplace=True)

    # Разделим на сток и спот
    stock_data = data.iloc[:, -1]
    spot_data = data.iloc[:, 0]

    # Инициализируем гиперпараметры найденные pmarima
    with open(f'./models/ar_stock_{metall_dict[key_route]}.pkl', 'rb') as pkl_stock:
        stock_params = pickle.load(pkl_stock)
    p_stock = stock_params['order'][0]
    q_stock = stock_params['order'][2]

    with open(f'./models/ar_spot_{metall_dict[key_route]}.pkl', 'rb') as pkl_stock:
        stock_params = pickle.load(pkl_stock)
    p_spot = stock_params['order'][0]
    q_spot = stock_params['order'][2]

    # Начнем моделировать используя параметры из исследования

    # STOCK________________________________________________________________
    model_garch_stock = arch_model(
        stock_data, vol='GARCH', p=p_stock, q=q_stock, rescale=True).fit(disp='off')

    # Произведем прогноз с горизонотом равным 90 дней
    forecast_garch_stock = model_garch_stock.forecast(horizon=90)

    # Выделим спрогнозированную дисперсию
    forecast_variance_stock = forecast_garch_stock.variance.values[-1]

    # Генерация случайных значений с нулевым средним и прогнозируемой дисперсией
    corr_values_stock = np.random.normal(
        loc=0, scale=np.sqrt(forecast_variance_stock))

    corr_values_stock = pd.DataFrame(corr_values_stock)

    # Отправляем в очередь корректировки прогноза (AR) запасов используя волатильность
    channel.basic_publish(
        exchange='',
        routing_key=f'stock_ar_{key_route}_queue',
        body=json.dumps({
            'id': key_route,
            'body': corr_values_stock.to_json()}
        )
    )
    print(corr_values_stock)
    #print(f"Upload on Stock_AR {key_route} completed successfully")

    # SPOT________________________________________________________________
    model_garch_spot = arch_model(
        spot_data, vol='GARCH', p=p_spot, q=q_spot, rescale=True).fit(disp='off')

    # Произведем прогноз с горизонотом равным 90 дней
    forecast_garch_spot = model_garch_spot.forecast(horizon=90)

    # Выделим спрогнозированную дисперсию
    forecast_variance_spot = forecast_garch_spot.variance.values[-1]

    # Генерация случайных значений с нулевым средним и прогнозируемой дисперсией
    corr_values_spot = np.random.normal(
        loc=0, scale=np.sqrt(forecast_variance_spot))

    corr_values_spot = pd.DataFrame(corr_values_spot)

    # Отправляем в очередь корректировки прогноза спотовой цены (DT) используя волатильность
    channel.basic_publish(
        exchange='',
        routing_key=f'stock_ar_{key_route}_garch_queue',
        body=json.dumps({
            'id': key_route,
            'body': corr_values_spot.to_json()}
        )
    )
    print(corr_values_spot)
    #print(f"Upload on Spot_DT {key_route} completed successfully")


if __name__ == '__main__':
    # Создание подключения к RabbitMQ
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Создание очередей для получения сообщений
    for i in metall:
        channel.queue_declare(queue=f'garch_{i}_queue')

    # Создание очередей для отправки сообщений
    for i in metall:
        channel.queue_declare(queue=f'stock_ar_{i}_garch_queue')

    for i in metall:
        channel.queue_declare(queue=f'spot_dt_{i}_garch_queue')

    for key in metall:
        channel.basic_consume(
            queue=f'garch_{key}_queue',
            on_message_callback=callback,
            auto_ack=True
        )

    print('...Ожидание сообщений, для выхода нажмите CTRL+C')
    channel.start_consuming()
