# -*- coding:utf-8 -*-
import json
import os
import time

import baostock as bs
import matplotlib
import numpy as np
import pandas as pd
from loguru import logger
from matplotlib import pyplot as plt

from mystock.backtrader import get_return
from mystock.settings import START_DATE, DUMP_DIR

matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体
matplotlib.rcParams['axes.unicode_minus'] = False  # 正常显示负号

# /home/rhino/s/a/_YYYY-MM-DD_HH-mm-ss_ssssss.log
logger.add(os.path.join(DUMP_DIR, '_{time:YYYYMMDD}.log'),
           rotation="50 MB",
           retention="3 days",
           compression="gz",
           enqueue=True)


def get_k_data(stock_code, stock_name):
    """
    获取从 2018-01-01 到昨天的历史交易日数据
    :param stock_code: sh.601398
    :param stock_name: 工商银行
    :return:
    """
    rs = bs.query_history_k_data_plus(stock_code,
                                      "date,code,high,low,open,close",
                                      start_date=START_DATE, end_date=None,
                                      frequency="d", adjustflag="3")

    # 转换为 DataFrame
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    df = pd.DataFrame(data_list, columns=rs.fields)

    df.to_csv(f"{os.path.join(DUMP_DIR, stock_code)}_{stock_name}.csv")

    # # 转换数据类型（high 和 low 默认为字符串，需要转成 float 才能比较）
    # df["high"] = df["high"].astype(float)
    # df["low"] = df["low"].astype(float)
    #
    # max_high_row = df.loc[df["high"].idxmax()]
    # min_low_row = df.loc[df["low"].idxmin()]
    #
    # print(f"最高价: {max_high_row['high']}，日期: {max_high_row['date']}")
    # print(f"最低价: {min_low_row['low']}，日期: {min_low_row['date']}")
    #
    # # akshare 的接口太慢了，走网络从东财实时获取
    # df = ak.stock_zh_a_hist(symbol=stock_code,
    #                         period="daily",
    #                         start_date="20180101",
    #                         # end_date="20250714",
    #                         adjust="qfq")  # 前复权
    #
    # df.to_csv(f"{os.path.join(DUMP_DIR, stock_code)}_{stock_name}.csv")


def get_distribution(stock_code, stock_name):
    # 1. 读取收盘价数据
    df = pd.read_csv(f"{os.path.join(DUMP_DIR, stock_code)}_{stock_name}.csv")
    # 收盘价
    prices = df['close']

    # 3. 动态计算 bin 宽度（建议使用均价的 2%）
    mean_price = prices.mean()
    bin_width = mean_price * 0.02
    min_price, max_price = prices.min(), prices.max()

    bins = np.arange(min_price, max_price + bin_width, bin_width)

    # 4. 使用 pd.cut 分组统计频次
    price_bins = pd.cut(prices, bins=bins, right=False)
    freq = price_bins.value_counts().sort_index()

    # 5. 输出停留时间最多的区间
    top_zone = freq.idxmax()
    top_days = freq.max()
    logger.info(f"{stock_code}_{stock_name} 最密集价格区间：{top_zone}, "
                f"共停留了 {top_days} 天")

    # 6. 输出覆盖70%时间的“价值区间”
    cum_freq = freq.sort_values(ascending=False).cumsum()
    total_days = freq.sum()
    value_area = freq[cum_freq <= 0.7 * total_days]

    # print("覆盖70%交易日的价值区间：")
    # print(value_area.sort_index())

    # 6. “价值区间”最低价、最高价
    lowest_price = value_area.index[0].left
    highest_price = value_area.index[-1].right

    # 7. 价值区间交易日合计
    total_days_in_value_area = value_area.sum()
    # print(f"覆盖比例：{total_days_in_value_area / total_days:.2%}")
    # 覆盖比例就不用输出了，肯定接近于 70%。因为计算的就是覆盖 70% 交易日的价值区间
    logger.info(f"{stock_code}_{stock_name} "
                f"覆盖70%交易日的价值区间：[{lowest_price}, {highest_price}), "
                f"共停留了 {total_days_in_value_area} 天, "
                f"总交易日 {total_days} 天）")

    # 7. 当前价格在历史分布的百分位
    current_price = prices.iloc[-1]
    percentile = (prices < current_price).sum() / len(prices) * 100
    logger.info(f"{stock_code}_{stock_name} 当前价格：{current_price:.2f}，"
                f"位于历史分布的第 {percentile:.2f} 百分位")

    # 8. 两个区间的最低价买入，回溯收益和回撤
    get_return(stock_code, stock_name, top_zone.left)
    get_return(stock_code, stock_name, lowest_price)

    # 8. 可视化频次分布
    freq.plot(kind='bar', figsize=(16, 6))
    plt.title(f"{stock_code}_{stock_name} 自 {START_DATE} 日股价停留分布")
    plt.xlabel("价格区间（元）")
    plt.ylabel("停留天数")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def get_top_100_companies():
    with open('top.json', encoding='utf-8') as f:
        return json.loads(f.read())


def login():
    """
    登入
    :return:
    """
    bs.login()


def logout():
    """
    登出
    :return:
    """
    bs.logout()


if __name__ == '__main__':
    login()

    cs = get_top_100_companies()

    for comp in cs:
        cs_code = comp.get('code')
        cs_name = comp.get('name')
        cs_mkt = comp.get('market')

        get_k_data(f"{cs_mkt}.{cs_code}", cs_name)
        get_distribution(f"{cs_mkt}.{cs_code}", cs_name)

        time.sleep(10)

    logout()
