import numpy as np
import pandas as pd


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


if __name__ == '__main__':
    for metall in metall_dict.keys():
        # Датафрейм авторегрессии
        ar_df = pd.read_csv(
            f'./results/intermediate/spot_ar_prognosis_{metall}.csv', sep=',', parse_dates=['index'], index_col=0)

        ar_df = ar_df.rename(columns={ar_df.columns.to_list()[0]: 'AutoReg'})

        ar_df = pd.DataFrame(ar_df.iloc[:, 0])

        ar_month_data = conf_int_month(ar_df, 'AutoReg')
        ar_quarter_data = conf_int_quarter(ar_df, 'AutoReg')

        result_ar = pd.concat([ar_month_data, ar_quarter_data], axis=0)
        result_ar = result_ar.round()

        # Датафрейм дерева решений
        dt_df = pd.read_csv(
            f'./results/intermediate/spot_dt_prognosis_{metall}.csv', sep=',', parse_dates=['index'], index_col=0)

        dt_df = dt_df.rename(
            columns={dt_df.columns.to_list()[0]: 'Decision_tree'})

        dt_df = pd.DataFrame(dt_df.iloc[:, 0])

        dt_month_data = conf_int_month(dt_df, 'Decision_tree')
        dt_quarter_data = conf_int_quarter(dt_df, 'Decision_tree')

        result_dt = pd.concat([dt_month_data, dt_quarter_data], axis=0)
        result_dt = result_dt.round()

        # Консолидирующая таблица

        adj_df = pd.concat(
            [ar_df, dt_df], axis=1)

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
            f'./final/result_{metall}.csv', sep=',')

        print(f'Model {metall} finished. Uploaded on local machine')
