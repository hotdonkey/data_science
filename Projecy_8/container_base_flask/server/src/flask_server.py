import json
import pika
from flask import Flask
import numpy as np
import pandas as pd


app = Flask(__name__)


@app.route('/')
def index():
    return "Test message. The server is running. Use entry points: /db_push or /prognosis"


@app.route('/db_push')
def db_push():
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


@app.route('/prognosis')
def prognosis():
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
        ar_quarter_data = conf_int_quarter(data_ar, 'AutoReg')

        result_ar = pd.concat([ar_month_data, ar_quarter_data], axis=0)
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
        dt_quarter_data = conf_int_quarter(data_dt, 'Decision_tree')

        result_dt = pd.concat([dt_month_data, dt_quarter_data], axis=0)
        result_dt = result_dt.round()

        # Консолидирующая таблица

        adj_df = pd.concat(
            [data_ar, data_dt], axis=1)

        adj_df['Final'] = np.mean(
            [adj_df['AutoReg'], adj_df['Decision_tree']], axis=0)
        adj_df.dropna(inplace=True)

        adj_df = pd.DataFrame(adj_df.iloc[:, -1])

        adj_month = conf_int_month(adj_df, 'Final')
        adj_quarter = conf_int_quarter(adj_df, 'Final')

        result_adj = pd.concat([adj_month, adj_quarter], axis=0)
        result_adj = result_adj.round()

        model_result = pd.concat([result_ar, result_dt, result_adj], axis=1)

        model_result.to_csv(
            f'./results/final/result_{metall}.csv', sep=',')

        return f'Model {metall} finished. Uploaded on local machine'


# Run the Flask application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
