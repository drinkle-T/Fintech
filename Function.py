# base on ** numpy **

# 每列是一个变量（股票），每行是一个观察值（日期）
import numpy as np
from sympy import symbols, solve
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import pandas as pd

'''
公司理财课上讲述的估值方法实操
'''


def profit(data):
    return


def profit_expect(weight, data):
    '''
    投资收益--期望
    :param weight:收益产生概率，若是历史的每月数据，则相等
    :param data: 收益数据
    :return: numpy
    '''
    return np.dot(weight.T, data)


def risk(weight, data):
    '''
    投资风险--标准差
    :param weight:收益产生概率，若是历史的每月数据，则相等
    :param data: 收益数据
    :return: numpy
    '''
    sigma = np.sqrt(profit_expect(weight, (data - profit_expect(weight, data)) ** 2))
    return sigma


def portfolios_profit(portfolios_weight, portfolios_expect):
    '''
    投资组合的加权平均收益
    :param portfolios_weight:投资组合的权重
    :param portfolios_expect: 每项投资的期望收益
    :return:
    '''
    return profit_expect(portfolios_weight, portfolios_expect)


def portfolios_risk(portfolios_weight, weight, data):
    '''
    通过协方差来计算投资组合的风险
    :param portfolios_weight: 投资组合的权重
    :param weight: 投资收益的权重，若是月份数据则权重均等
    :param data:投资数据
    :return:一个值
    '''
    cov = np.cov(data.T, aweights=weight, ddof=1)
    # print('the shape of the cov is :{} ,and the cov is \n {}'.format(cov.shape,cov))
    sigma = 0
    for i in range(cov.shape[0]):
        for j in range(i, cov.shape[1]):
            # print('now is {} and {}'.format(i,j))
            sigma += cov[i][j] * portfolios_weight[j] * portfolios_weight[i]
    return np.sqrt(sigma)


def Beta(portfolios_weight, weight, data, market_data):
    if portfolios_weight is None:
        beta = np.cov(data, market_data, aweights=weight, ddof=1)[0, 1] / risk(weight, market_data)
    else:
        beta_list = []
        # data = data.reshape(data.shape[0], -1)
        # print('the data shape is {}'.format(data.shape))
        for i in range(data.shape[1]):
            beta_list.append(np.cov(data[:, i], market_data, aweights=weight, ddof=1)[0, 1] / risk(weight, market_data))
        beta_list = np.array(beta_list)
        beta = np.dot(beta_list.T, portfolios_weight)
    return beta


# 债券利息需要完善
def bond_profit(issue_price, par_value, interest, time):
    '''
    计算的是一般债券，非永久，利息固定
    :param issue_price: 发行价格
    :param par_value: 票面价格
    :param interest: 利息
    :param time: 期数
    :return: 利率，float
    '''
    k = symbols('k')
    P = issue_price
    B_0 = par_value
    i = interest
    n = time
    eq = P - B_0 * i * (1 - (1 + k) ** (-n)) / k - B_0 * (1 + k) ** (-n)
    result = solve(eq, k)
    return result[0].evalf()


def get_g(PEG, PE):
    '''
    利润增速可以用市盈率/PEG得到
    :param PEG:
    :param PE: 市盈率
    :return:
    '''
    return PE / PEG


def get_ROE(PE, PBV):
    return PBV / PE


def Gorden_profit(bonus, issue_value, g):
    '''
    长期持有股票的收益率。要求：1、成长率需固定 2、分红  3、k > g
    :param bonus: 分红
    :param issue_value: 票面价格
    :param g: 增速（用拟合值）
    :return:
    '''
    return bonus * (1 + g) / issue_value + g


def PE_filter(data_arg, fig=False):
    '''
    在g/PE的坐标轴中，选择g>mean*1.5,PE<mean的股票
    :param data_arg: 计算出g，并且已经完成均值聚合
    :param fig: 是否进行绘图，默认为否
    :return:index数据，通过筛选的股票列表，需要用sort_values()排序
    '''
    # 对PE,g进行缩尾处理
    # print('raw data shape is ',data_arg.shape)
    data = data_arg.sort_values(by='PE_stock', ascending=False)
    data = data.drop(data.index[:round(data.shape[0] * 0.3)])
    data = data.sort_values(by='PE_stock', ascending=True)
    data = data.drop(data.index[:round(data.shape[0] * 0.3)])
    pe_mean = data['PE_stock'].mean()
    # print('after two drop data is',data.shape)

    data = data.sort_values(by='g_stock', ascending=False)
    data = data.drop(data.index[:round(data.shape[0] * 0.1)])
    data = data.sort_values(by='g_stock', ascending=True)
    data = data.drop(data.index[:round(data.shape[0] * 0.1)])
    g_mean = data['g_stock'].mean()
    # print('after two drop data is',data.shape)

    # 市盈率法,同时进行绘图,原打算用拟合值，然后通过移动拟合线进行筛选，但是垃圾股对于拟合线的影响太大，以至于拟合线法效果不好
    # 此处直接使用均值四分位进行筛选
    good_stock = []
    if fig == True:
        model = LinearRegression()
        x_1 = data['PE_stock'].values.reshape(-1, 1)
        y_1 = data['g_stock'].values.reshape(-1, 1)
        model.fit(x_1, y_1)
        plt.scatter(x_1, y_1)
        plt.plot(x_1, model.predict(x_1), color='red')
        plt.plot(x_1, model.predict(x_1) * 1.5, color='b')
        plt.plot(x_1, model.predict(x_1) * 0.5, color='b')
        plt.xlabel('PE')
        plt.ylabel('G')
        plt.show()

    # data['g_pred'] = model.predict(x_1)
    # print(data.head(40))
    # good_stock = data[(data['g_stock'] > data['g_pred'] * 1.5) &
    # (data['stock_value'] > 5)&(data['stock_value'] < 20)].index
    good_stock = data[(data['g_stock'] > g_mean * 1.5) & (data['PE_stock'] < pe_mean)].index
    print('通过PE筛选条件的股票有{}个'.format(len(good_stock)))
    return good_stock


def PBV_filter(data_arg, fig=False):
    '''
    在g/PE的坐标轴中，选择g>mean*1.5,PE<mean的股票
    :param data_arg: 计算出g，并且已经完成均值聚合
    :param fig: 是否进行绘图，默认为否
    :return:index数据，通过筛选的股票列表，需要用sort_values()排序
    '''
    # 对PE,g进行缩尾处理
    # print('raw data shape is ',data_arg.shape)
    data = data_arg.sort_values(by='PB_stock', ascending=False)
    data = data.drop(data.index[:round(data.shape[0] * 0.3)])
    data = data.sort_values(by='PB_stock', ascending=True)
    data = data.drop(data.index[:round(data.shape[0] * 0.3)])
    pb_mean = data['PB_stock'].mean()
    # print('after two drop data is',data.shape)

    data = data.sort_values(by='ROE', ascending=False)
    data = data.drop(data.index[:round(data.shape[0] * 0.1)])
    data = data.sort_values(by='ROE', ascending=True)
    data = data.drop(data.index[:round(data.shape[0] * 0.1)])
    roe_mean = data['ROE'].mean()
    # print('after two drop data is',data.shape)

    # 市盈率法,同时进行绘图,原打算用拟合值，然后通过移动拟合线进行筛选，但是垃圾股对于拟合线的影响太大，以至于拟合线法效果不好
    # 此处直接使用均值四分位进行筛选
    good_stock = []
    model = LinearRegression()
    x_1 = data['PB_stock'].values.reshape(-1, 1)
    y_1 = data['ROE'].values.reshape(-1, 1)
    model.fit(x_1, y_1)
    if fig == True:
        plt.scatter(x_1, y_1)
        plt.plot(x_1, model.predict(x_1), color='red')
        plt.plot(x_1, model.predict(x_1) * 2, color='b')
        plt.plot(x_1, model.predict(x_1) * 0.5, color='b')
        plt.xlabel('PBV')
        plt.ylabel('ROE')
        plt.show()

    data['ROE_pred'] = model.predict(x_1)
    good_stock = data[
        (data['ROE'] >= data['ROE_pred'] * 2)].index  # &(data['stock_value'] > 5)&(data['stock_value'] < 20)
    # good_stock = data[(data['roe_stock'] > roe_mean * 1.5) & (data['PB_stock'] < pb_mean)].index
    print('通过PBV筛选条件的股票有{}个'.format(len(good_stock)))
    return good_stock


def CAPM(market_data, stock_data, fig=False):
    '''
    该函数尚未完善
    :param market_data:
    :param stock_data:
    :param fig:
    :return:
    '''
    # 数据清洗
    market_data = market_data.replace('-', None)
    stock_data = stock_data.replace('-', None)
    market_data['Flow'] = pd.to_numeric(market_data['Flow'], errors='coerce')  # 将数据转换为float，并将无法转换的数据变为Nan
    stock_data['stock_value'] = pd.to_numeric(stock_data['stock_value'], errors='coerce')
    market_data = market_data.dropna()
    stock_data = stock_data.dropna()
    pass
