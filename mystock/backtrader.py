# -*- coding:utf-8 -*-
import os.path

import akshare as ak
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from loguru import logger

from mystock.settings import START_DATE, DUMP_DIR

matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体
matplotlib.rcParams['axes.unicode_minus'] = False  # 正常显示负号

# /home/rhino/s/a/_YYYY-MM-DD_HH-mm-ss_ssssss.log
logger.add(os.path.join(DUMP_DIR, '_{time:YYYYMMDD}.log'),
           rotation="50 MB",
           retention="3 days",
           compression="gz",
           enqueue=True)

# 证券代码
STOCK_CODE = "sh.601939"
STOCK_NAME = "建设银行"

# 目标买入价
BID_PRICE = 7

# 上涨 20% 卖出
SELL_RATE = 1.2


def get_max_drawdown(equity_series):
    """
    计算最大回撤
    :param equity_series:
    :return:
    """
    roll_max = equity_series.cummax()
    drawdown = equity_series / roll_max - 1
    max_dd = drawdown.min()
    return max_dd


def get_return(stock_code=STOCK_CODE, stock_name=STOCK_NAME, bid_price=BID_PRICE):
    # # 1. 获取万华化学的历史数据（前复权）
    df = pd.read_csv(f"{os.path.join(DUMP_DIR, stock_code)}_{stock_name}.csv")
    df.set_index("date", inplace=True)

    # 2. 筛选 2018-01-01 以后的数据
    df = df[df.index >= START_DATE]

    # 3. 初始化变量
    capital = 1  # 初始资金 = 1
    holding = False
    buy_price = 0
    equity_curve = []

    # 4. 模拟交易
    for date, row in df.iterrows():
        price = row["close"]

        if not holding:
            if price < bid_price:
                buy_price = price
                holding = True

        else:
            if price >= buy_price * SELL_RATE:
                capital *= price / buy_price  # 卖出盈利
                holding = False

        # 记录每日资金曲线
        equity_curve.append(capital if not holding else capital * price / buy_price)
    df["equity"] = equity_curve

    # 5. 可视化
    df[["close", "equity"]].plot(figsize=(12, 6))
    plt.title(f"{stock_code}_{stock_name} 策略回测（<{bid_price} 买，+20% 卖）")
    plt.ylabel("价格 / 策略净值")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # 计算总收益、年化、最大回撤
    total_return = df["equity"].iloc[-1] - 1
    trading_days = len(df)
    annual_return = (df["equity"].iloc[-1]) ** (252 / trading_days) - 1
    max_drawdown = get_max_drawdown(df["equity"])
    # 输出指标
    logger.info(f"买入价：{bid_price}，"
                f"总收益率: {total_return:.2%}，"
                f"年化收益率: {annual_return:.2%}，"
                f"最大回撤: {max_drawdown:.2%}")


if __name__ == '__main__':
    get_return()
