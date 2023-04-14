import csv

import numpy as np
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from lxml import etree
import re
import random
import time
from Selenium_Hyper import Market_page_num, stock_page_num, do_save
import urllib.request
import unicodedata


class selenium_scrapy(object):
    '''
    在东方财富网上爬取近几个月的股票市盈率、市现率等指标
    '''
    driver_path = r"C:\Users\drinkle\AppData\Local\Google\Chrome\Application\chromedriver_111\chromedriver.exe"

    #  可加入代理ip
    def __init__(self, url):
        self.url = url
        self.driver = webdriver.Chrome(executable_path=self.driver_path)

    def run(self, if_stock=False):
        self.driver.get(self.url)
        all_stock_date = []
        all_market = []
        # page_num = 1

        # 爬取前几页的Market信息，Market信息的详情页中有Stock信息
        for page_num in range(1, Market_page_num + 1):
            print('-----------the number of the Page is {}-----------'.format(page_num))
            WebDriverWait(driver=self.driver, timeout=300).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="scgz_table"]//tbody')))
            self.driver.switch_to.window(self.driver.window_handles[0])
            source = self.driver.page_source
            markets = self.market_condition(source)  # 提取这一页的market HTML 内容
            all_market.append(markets)
            if if_stock == True:
                for n, market in enumerate(markets):
                    # 每天的详情页都打开爬取stock数据
                    print('the num of the Market in this page is {}'.format(n))
                    print('the Process in the Market page is {:.0f}%'.format(n / len(markets) * 100))
                    el = WebDriverWait(driver=self.driver, timeout=300).until(
                        EC.presence_of_element_located((By.XPATH,
                                                        '//*[@id="scgz_table"]/div[2]/div[2]/table/tbody/tr[{}]/td[2]/a'.format(
                                                            n + 1))))
                    detail_url = self.driver.find_element_by_xpath(
                        '//*[@id="scgz_table"]/div[2]/div[2]/table/tbody/tr[{}]/td[2]/a'.format(n + 1))
                    self.driver.execute_script("arguments[0].click();", el)  # 打开当天详情页
                    time.sleep(random.choice(range(2, 3)))
                    self.driver.switch_to.window(self.driver.window_handles[1])  # 切换到打开的页面
                    detail_sourse = self.driver.page_source  # 获取详情页的股票html
                    all_stock_date.append(self.stock_condition(detail_sourse, market['date']))
                    # print(market['date'])

                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])

            self.driver.switch_to.window(self.driver.window_handles[0])
            market_next_page = self.driver.find_element_by_xpath \
                ('//*[@id="scgz_table"]/div[3]/div[1]/a[@data-page="{}"]'.format(page_num + 1))  # 获得`下一步`的按钮

            # print('the page is {},the page detail is {} '.format(page_num, market_next_page))
            market_next_page.click()  # 则点击下一页
            time.sleep(random.choice(range(2, 4)))
            # self.driver.close()   #这里click并没有产生新窗口，因此不需要close
            # self.driver.switch_to.window(self.driver.window_handles[0])

        self.driver.quit()
        return all_stock_date, all_market

    def market_condition(self, sourse):
        '''
        目前只有一页的市场情况，天数不多
        :param sourse: 市场界面
        :return:返回每天的市场情况
        '''
        html = etree.HTML(sourse)
        market_list = html.xpath('//*[@id="scgz_table"]/div[2]/div[2]/table/tbody//tr')
        market_detail = []
        rec = re.compile(r'[\d .]+', re.S)
        for n, market in enumerate(market_list):
            date = market.xpath('.//td[@class="desc_col"]/text()')[0]
            PE_market = market.xpath('.//td[3]/text()')[0]
            # PE_market = rec.findall(PE_market)[0]
            General_capital = market.xpath('.//td[4]/text()')[0]
            General_capital = rec.findall(General_capital)[0]
            Circul_capital = market.xpath('.//td[5]/text()')[0]
            Circul_capital = rec.findall(Circul_capital)[0]
            Total_value = market.xpath('.//td[6]/text()')[0]
            Total_value = rec.findall(Total_value)[0]
            Circul_value = market.xpath('.//td[7]/text()')[0]
            Circul_value = rec.findall(Circul_value)[0]
            Number_stocks = market.xpath('.//td[8]/text()')[0]
            Value = market.xpath('.//td[9]/span/text()')[0]
            Flow = market.xpath('.//td[10]/span/text()')[0]
            detail = {"date": date, "PE_market": PE_market, "General_capital": General_capital,
                      "Circul_capital": Circul_capital,
                      "Total_value": Total_value, "Circul_value": Circul_value, "Number_stocks": Number_stocks,
                      'Value': Value, 'Flow': Flow}
            market_detail.append(detail)

        return np.array(market_detail)

    def stock_condition(self, sourse, date):
        '''
        目前只有一页
        :param sourse: 具体某天的股票详情页数据
        :param date: 某天
        :return: 返回某天的所有股票数据
        '''
        stock_detail = []
        self.driver.switch_to.window(self.driver.window_handles[1])

        for page_num in range(1, stock_page_num):
            if page_num % 10 == 0:
                # 计数
                print('the Process of the stock is {:.0f}%'.format(page_num / stock_page_num * 100))

            WebDriverWait(driver=self.driver, timeout=300).until(
                EC.presence_of_element_located((By.XPATH,
                                                '//*[@id="gggz_table"]/div[2]/div[2]/table/tbody/tr//td[2]/a')))

            source_stock = self.driver.page_source
            if page_num == 1:
                html = etree.HTML(sourse)
            else:
                html = etree.HTML(source_stock)

            stock_list = html.xpath('//*[@id="gggz_table"]/div[2]/div[2]/table/tbody/tr')  # 找到信息条列
            # print('the len of the stock list is ', len(stock_list))
            for stock in stock_list:
                stock_id = stock.xpath('.//td[2]/a/text()')[0]
                stock_value = stock.xpath('.//td[5]/span/text()')[0]
                stock_flow = stock.xpath('.//td[6]/span/text()')[0]
                PE_stock = stock.xpath('.//td[7]/text()')[0]
                PB_stock = stock.xpath('.//td[9]/text()')[0]
                PEG_stock = stock.xpath('.//td[10]/text()')[0]
                PS_stock = stock.xpath('.//td[11]/text()')[0]

                detail = {"date": date, "stock_id": str(stock_id), "stock_value": stock_value, 'stock_flow': stock_flow,
                          "PE_stock": PE_stock, "PB_stock": PB_stock, "PEG_stock": PEG_stock, "PS_stock": PS_stock}
                stock_detail.append(detail)

            el = WebDriverWait(driver=self.driver, timeout=300).until(
                EC.presence_of_element_located((By.XPATH,
                                                '//*[@id="gggz_table"]/div[3]/div[1]/a[@data-page="{}"]'.format(
                                                    page_num + 1))))
            stock_next_page = self.driver.find_element_by_xpath \
                ('//*[@id="gggz_table"]/div[3]/div[1]/a[@data-page="{}"]'.format(page_num + 1))  # 获得`下一步`的按钮
            self.driver.execute_script("arguments[0].click();", el)  # 则点击下一页
            time.sleep(random.choice(range(2, 3)))
            # self.driver.close()   #这里click并没有产生新窗口，因此不需要close
            # self.driver.switch_to.window(self.driver.window_handles[1])
        print('--' * 50)
        return np.array(stock_detail)
        pass


def save_data(data, name, do=False):
    # print(stock_data[0],type(stock_data[0]))
    # print(market_data[0],type(market_data[0]))
    if do == True:
        headers = list(data[0].keys())
        with open('{}.csv'.format(name), 'w', encoding='utf-8', newline='') as fp:
            writer = csv.DictWriter(fp, headers)
            writer.writeheader()
            writer.writerows(data)

    else:
        return


if __name__ == '__main__':
    url = "https://data.eastmoney.com/gzfx/scgk.html"
    pachong = selenium_scrapy(url)
    stock_data, market_data = pachong.run()
    # print(stock_data)
    stock_data = np.array(stock_data).reshape(-1, )
    market_data = np.array(market_data).reshape(-1, )
    # print(stock_data.shape)
    # print(market_data.shape)

    # save_data(stock_data,'Stock_Data',do=do_save)
    save_data(market_data, 'Market_Data', do=do_save)
