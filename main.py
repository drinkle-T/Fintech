import numpy as np
from Function import *
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression


def portfolio_test():
    weight = [0.25, 0.5, 0.25]
    data = [[0.1, 0.14, 0.16], [0.09, 0.13, 0.18], [0.14, 0.12, 0.1]]
    portfolios_weight = [0.333, 0.333, 0.333]
    # market_data = [-0.2, 0.1, 0.15, 0.2, 0.25]
    weight = np.array(weight)
    data = np.array(data)
    data = data.T
    # market_data = np.array(market_data)
    portfolios_weight = np.array(portfolios_weight)

    print(weight.shape, 'data is {}'.format(data))
    # print(data[:,2])
    print('the cov of AB is ', np.cov(data[:, [0, 2]].T))

    E = profit_expect(weight, data)
    print('the expect profit of the stock is ', E, type(E))
    # print('the expect profit of the market is ', profit_expect(weight, market_data))

    V = risk(weight, data)
    print('the risk of the stock is ', V, type(V))
    # print('the risk of the market is ', risk(weight, market_data))

    print('the portfolios profit is', portfolios_profit(portfolios_weight, profit_expect(weight, data)))
    print('the risk of the portfolios is ', portfolios_risk(portfolios_weight, weight, data))

    # print('the beta is ', Beta(None, weight, data, market_data))
    # print('the profit of the bond is ', bond_profit(108, 100, 0.05, 10))


def pandas_test():
    # 对爬取的股票数据进行预处理测试
    value_columns = ['stock_value', 'PE_stock', 'PB_stock', 'PEG_stock', 'PS_stock']
    data = pd.read_csv('./Stock_Data.csv')
    data = data.replace('-', None)
    # 数据筛选,
    # drop_index1 = data[(data['stock_id'] == 300102) | (data['stock_id'] == 600766) | (data['stock_id'] == 688176) | (
    #             data['stock_id'] == 601069)].index
    # print(drop_index1)
    # data = data.drop(drop_index1)
    data['PE_stock'] = pd.to_numeric(data['PE_stock'], errors='coerce')  # 将数据转换为float，并将无法转换的数据变为Nan
    data['PS_stock'] = pd.to_numeric(data['PS_stock'], errors='coerce')
    data[value_columns] = data[value_columns].astype('float')
    drop_index2 = data[data['PEG_stock'] == 0.0].index
    data = data.drop(drop_index2)
    data = data.dropna()
    # 加入g,ROE
    data['g_stock'] = get_g(PE=data['PE_stock'], PEG=data['PEG_stock'])
    data['ROE'] = get_ROE(PE=data['PE_stock'], PBV=data['PB_stock'])
    extra_columns = ['g_stock', 'ROE']
    # print(data.head())
    # print(data.astype('category').describe())

    # 按照时间进行聚合
    data_arg = data[value_columns + ['stock_id'] + extra_columns].groupby('stock_id').mean()
    # print(data_arg.head())

    return data_arg


if __name__ == '__main__':
    # value_columns = ['stock_value', 'PE_stock', 'PB_stock', 'PEG_stock', 'PS_stock']
    pd.set_option('display.width', None)
    portfolio_test()
    data_arg = pandas_test()
    filter = True  #是否进行股票筛选
    IF_plot = True  #是否进行股票筛选的绘图展示
    market_test = False  #是否进行CAPM模型的市场测试
    if filter == True:
        pe_list = PE_filter(data_arg, IF_plot).values
        pbv_list = PBV_filter(data_arg, IF_plot).values
        best_choice = []
        for i in pe_list:
            if i in pbv_list:
                best_choice.append(i)
        print(best_choice)
        print(pe_list)
        print(pbv_list)
        # print(pbv_list.sort_values())
        # print(pe_list.sort_values())
    if market_test == True:
        market_data = pd.read_csv('./Market_Data.csv')
        stock_data = pd.read_csv('./Stock_Data.csv')
        CAPM(market_data, stock_data)
        pass
