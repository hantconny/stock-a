# -*- coding:utf-8 -*-
"""
从 backtrader.json 文件读取需要分析的证券代码（个股或 ETF）
走 akshare 的东财接口获取历史交易数据，vpn 下东财会断连，需使用国内网络
根据 settings.py 中配置的起始时间，回溯每日收盘价格
找出
- 停留时间最多的区间
- 覆盖70%时间的“价值区间”
- 当前价格在历史分布的百分位
- 模拟 停留时间最多的区间 的最低价买入，回溯收益和回撤
- 模拟 覆盖70%时间的“价值区间” 的最低价买入，回溯收益和回撤
"""
import os
import time

import akshare as ak
import matplotlib
import numpy as np
import pandas as pd
from loguru import logger
from matplotlib import pyplot as plt

import json
from backtrader import get_return
from settings import START_DATE, DUMP_DIR, STOCK_CODE, STOCK_NAME, PLOT, TODAY
from utils import clear_file

matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体
matplotlib.rcParams['axes.unicode_minus'] = False  # 正常显示负号

# /home/rhino/s/a/app_YYYY-MM-DD_HH-mm-ss_ssssss.log
logger.add(os.path.join(DUMP_DIR, 'app_{time:YYYYMMDD}.log'),
           rotation="50 MB",
           retention="3 days",
           compression="gz",
           enqueue=True)


def get_k_data(stock_code=STOCK_CODE, stock_name=STOCK_NAME):
    """
    获取从 2018-01-01 到昨天的历史交易日数据
    :param stock_code: 如 588000 或 601398
    :param stock_name: 如 科创50 或 工商银行
    :return:
    """
    df = ak.fund_etf_hist_em(symbol=stock_code,
                             start_date=START_DATE.replace('-', ''),
                             end_date=TODAY.replace('-', ''),
                             period="daily",
                             adjust="qfq")

    df = df.rename(columns={"收盘": "close", "日期": "date"})

    df.to_csv(f"{os.path.join(DUMP_DIR, stock_code)}_{stock_name}.csv")


def get_distribution(stock_code=STOCK_CODE, stock_name=STOCK_NAME):
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

    if PLOT:
        # 8. 可视化频次分布
        freq.plot(kind='bar', figsize=(16, 6))
        plt.title(f"{stock_code}_{stock_name} 自 {START_DATE} 日股价停留分布")
        plt.xlabel("价格区间（元）")
        plt.ylabel("停留天数")
        plt.grid(True)
        plt.tight_layout()
        plt.show()


def get_stocks():
    """
    读取需要评估的证券信息
    :return:
    """
    with open('json/backtrader.json', encoding='utf-8') as f:
        return json.loads(f.read())


if __name__ == '__main__':
    cs = get_stocks()

    for comp in cs:
        cs_code = comp.get('code')
        cs_name = comp.get('name')
        # cs_mkt = comp.get('market')

        get_k_data(f"{cs_code}", cs_name)
        get_distribution(f"{cs_code}", cs_name)

        time.sleep(10)

    # 利用 settings.py 中的默认配置评估单个证券
    # get_k_data()
    # get_distribution()

    clear_file()
