import json
import pika
from flask import Flask
import numpy as np
import pandas as pd
import requests
import logging


app = Flask(__name__)

# Конфигурация логгирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/')
def index():
    return "Test message. The server is running. Use entry points: /parse (make your tea), /db_push, /prognosis"


@app.route('/parse')
def parse_data():
    try:
        # Список источников, нам понадобится информация по 5 видам сырья:
        # алюминий, медь, свинец, никель и цинк
        metalls = {
            'aluminium': 'Al', 'copper': 'Cu',
            'lead': 'Pb', 'nickel': 'Ni', 'zink': 'Zn'
        }

        def get_metalls(metall_name: str):

            # Запрос к источнику
            url = f'https://www.westmetall.com/en/markdaten.php?action=table&field=LME_{metalls[metall_name]}_cash'

            response = requests.get(url)

            # преобразуем ответ в датафрейм
            df_2023 = pd.read_html(response.text)[0]
            df_2022 = pd.read_html(response.text)[1]
            df_2021 = pd.read_html(response.text)[2]
            df_2020 = pd.read_html(response.text)[3]
            df_2019 = pd.read_html(response.text)[4]
            df_2018 = pd.read_html(response.text)[5]
            df_2017 = pd.read_html(response.text)[6]
            df_2016 = pd.read_html(response.text)[7]
            df_2015 = pd.read_html(response.text)[8]
            df_2014 = pd.read_html(response.text)[9]
            df_2013 = pd.read_html(response.text)[10]
            #
            df_2012 = pd.read_html(response.text)[11]
            df_2011 = pd.read_html(response.text)[12]
            df_2010 = pd.read_html(response.text)[13]
            df_2009 = pd.read_html(response.text)[14]
            df_2008 = pd.read_html(response.text)[15]

            df = pd.concat([
                df_2023, df_2022, df_2021,
                df_2020, df_2019, df_2018,
                df_2017, df_2016, df_2015,
                df_2014, df_2013, df_2012,
                df_2011, df_2010, df_2009,
                df_2008
            ]
            )

            # очищаем таблицу от неинформативных строк
            cleared_df = df[df['date'] != 'date']
            # заменяем символы пропусков нулями
            cleared_df = cleared_df.replace('-', 0)

            # приобразуем типы данных
            cleared_df['date'] = pd.to_datetime(cleared_df['date'])
            # т.к. столбцы имеют разное назание, обращяемся по индексу
            cleared_df.iloc[:, 1] = pd.to_numeric(
                cleared_df.iloc[:, 1])

            cleared_df.iloc[:, 2] = pd.to_numeric(
                cleared_df.iloc[:, 2])
            # в данном столбце, за счет использования символа запятой
            # для разделения целой части от дробной,
            # pandas не корректно преобразовал значения
            cleared_df.iloc[:, 3] = pd.to_numeric(
                cleared_df.iloc[:, 3]) / 1000

            cleared_df.set_index('date', inplace=True)

            cleared_df.to_csv(f'./data/{metall_name}.csv', sep=',')

        for metall in metalls.keys():
            # Получение данных
            get_metalls(metall)

        return 'Parsing completed successfully'

    except Exception as e:
        logger.error(f"An error occurred in parser: {str(e)}")
        return 'Error occurred while parsing database.'


@app.route('/db_push')
def db_push():
    try:
        def get_metalls(metall_name: str, channel):
            # Create a dataframe from the database
            data = pd.read_csv(
                f'./data/{metall_name}.csv',
                index_col='date',
                parse_dates=['date']
            )

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
            pika.ConnectionParameters('rabbitmq')
        )
        channel = connection.channel()

        # Declare the queue for sending messages
        channel.queue_declare(queue='raw_queue')

        metall = ['aluminium', 'copper', 'lead', 'nickel', 'zink']
        for target in metall:
            get_metalls(target, channel)

        # Close the connection to RabbitMQ
        connection.close()

        return 'Database push completed.'

    except Exception as e:
        logger.error(f"An error occurred in db_push: {str(e)}")
        return 'Error occurred while pushing to the database.'


@app.route('/prognosis')
def prognosis():
    try:
        metall_dict = {
            'aluminium': 'al', 'copper': 'cu',
            'lead': 'pb', 'nickel': 'nk', 'zink': 'zn'
        }

        def conf_int_month(data, name):
            prognosis_month = pd.DataFrame(data.groupby(
                pd.Grouper(freq='M')).mean())

            prognosis_month = prognosis_month.iloc[-4:, :]

            prognosis_month['std'] = pd.DataFrame(data.groupby(
                pd.Grouper(freq='M')).std())

            prognosis_month['num_days'] = pd.DataFrame(data.groupby(
                pd.Grouper(freq='M')).count())

            prognosis_month[f'{name}_min'] = prognosis_month[f'{name}'] - 1.96 * \
                (prognosis_month['std'] / np.sqrt(prognosis_month['num_days']))

            prognosis_month[f'{name}_max'] = prognosis_month[f'{name}'] + 1.96 * \
                (prognosis_month['std'] / np.sqrt(prognosis_month['num_days']))

            prognosis_month = prognosis_month.drop(
                ['std', 'num_days'], axis=1)

            return prognosis_month

        def conf_int_quarter(data, name):
            prognosis__q = pd.DataFrame(
                data.groupby(pd.Grouper(freq='Q')).mean())

            prognosis__q['std'] = pd.DataFrame(
                data.groupby(pd.Grouper(freq='Q')).std())

            prognosis__q['num_days'] = pd.DataFrame(
                data.groupby(pd.Grouper(freq='Q')).count())

            prognosis__q[f'{name}_min'] = prognosis__q[f'{name}'] - 1.96 * \
                (prognosis__q['std'] / np.sqrt(prognosis__q['num_days']))

            prognosis__q[f'{name}_max'] = prognosis__q[f'{name}'] + 1.96 * \
                (prognosis__q['std'] / np.sqrt(prognosis__q['num_days']))

            prognosis__q = prognosis__q.drop(columns=['std', 'num_days'])

            prognosis__q = prognosis__q.iloc[-1:, :]

            prognosis__q = prognosis__q.rename(
                index={prognosis__q.index[0]: 'Quarter'})

            return prognosis__q

        for metall in metall_dict.keys():
            # Датафрейм авторегрессии
            data_ar = pd.read_csv(
                f'./results/intermediate/spot_ar_prognosis_{metall}.csv', sep=',', parse_dates=['index'])

            data_ar = pd.DataFrame(data_ar.iloc[:, :2])
            data_ar = data_ar.rename(columns={
                data_ar.columns.to_list()[1]:
                'AutoReg', 'index': 'date'
            }
            )
            data_ar['dow'] = data_ar['date'].dt.day_of_week
            data_ar = data_ar[(data_ar['dow'] != 5) & (data_ar['dow'] != 6)]
            data_ar.drop(['dow'], axis=1, inplace=True)
            data_ar.set_index('date', inplace=True)

            ar_month_data = conf_int_month(data_ar, 'AutoReg')
            #ar_quarter_data = conf_int_quarter(data_ar, 'AutoReg')
            result_ar = pd.DataFrame(ar_month_data)
            #result_ar = pd.concat([ar_month_data, ar_quarter_data], axis=0)
            result_ar = result_ar.round()

            # Датафрейм дерева решений
            data_dt = pd.read_csv(
                f'./results/intermediate/spot_dt_prognosis_{metall}.csv', sep=',', parse_dates=['index'])

            data_dt = pd.DataFrame(data_dt.iloc[:, :2])
            data_dt = data_dt.rename(columns={
                data_dt.columns.to_list()[1]:
                'Decision_tree', 'index': 'date'
            }
            )
            data_dt['dow'] = data_dt['date'].dt.day_of_week
            data_dt = data_dt[(data_dt['dow'] != 5) & (data_dt['dow'] != 6)]
            data_dt.drop(['dow'], axis=1, inplace=True)
            data_dt.set_index('date', inplace=True)

            dt_month_data = conf_int_month(data_dt, 'Decision_tree')
            #dt_quarter_data = conf_int_quarter(data_dt, 'Decision_tree')
            result_dt = pd.DataFrame(dt_month_data)
            #result_dt = pd.concat([dt_month_data, dt_quarter_data], axis=0)
            result_dt = result_dt.round()

            # Консолидирующая таблица

            adj_df = pd.concat(
                [data_ar, data_dt], axis=1)

            adj_df['Final'] = np.mean(
                [adj_df['AutoReg'], adj_df['Decision_tree']], axis=0)
            adj_df.dropna(inplace=True)

            adj_df = pd.DataFrame(adj_df.iloc[:, -1])

            adj_month = conf_int_month(adj_df, 'Final')
            #adj_quarter = conf_int_quarter(adj_df, 'Final')
            result_adj = pd.DataFrame(adj_month)
            #result_adj = pd.concat([adj_month, adj_quarter], axis=0)
            result_adj = result_adj.round()

            model_result = pd.concat(
                [result_ar, result_dt, result_adj], axis=1)

            model_result.to_csv(
                f'./results/final/result_{metall}.csv', sep=',')

        return f'Model finished. Uploaded on local machine'

    except Exception as e:
        logger.error(f"An error occurred in prognosis: {str(e)}")
        return 'Error occurred while modeling prognosis.'


# Run the Flask application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
