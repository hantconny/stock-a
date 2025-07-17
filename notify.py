# -*- coding:utf-8 -*-
"""
从 hold.json 文件读取持仓证券代码
根据 settings.py 中配置的止盈百分比，回溯每日收盘价格
如果达到止盈位，则通过邮件和桌面文件进行提醒，希望他能看到
"""
import json
import os.path

import pandas as pd
from loguru import logger

from historical_range import get_k_data, login, logout
from settings import STOCK_CODE, STOCK_NAME, DUMP_DIR, TAKE_PROFIT
from utils import send_mail, dump_file

# /home/rhino/s/a/notify_YYYY-MM-DD_HH-mm-ss_ssssss.log
logger.add(os.path.join(DUMP_DIR, 'notify_{time:YYYYMMDD}.log'),
           rotation="50 MB",
           retention="3 days",
           compression="gz",
           enqueue=True)


def get_position():
    """
    读取持仓文件，该文件手动维护，没有自动接口读取当前持仓
    :return:
    """
    with open('json/position.json', encoding='utf-8') as f:
        return json.loads(f.read())


def get_watchlist():
    """
    读取自选文件，该文件手动维护
    :return:
    """
    with open('json/watchlist.json', encoding='utf-8') as f:
        return json.loads(f.read())


def get_sell_notify(_stock_code=STOCK_CODE, _stock_name=STOCK_NAME, _hold_price=0.0):
    """
    持仓卖出提醒
    :param _stock_code:
    :param _stock_name:
    :param _hold_price:
    :return:
    """
    df = pd.read_csv(f"{os.path.join(DUMP_DIR, _stock_code)}_{_stock_name}.csv")
    # 当天收盘价
    close_price = df.iloc[-1]['close']
    if close_price > _hold_price * TAKE_PROFIT:
        # 邮件内容
        subject = f"{_stock_code}_{_stock_name} 止盈提醒"
        content = (f"{_stock_code}_{_stock_name} 已达到设定的止盈价格"
                   f"\n持仓价格: {_hold_price}"
                   f"\n止盈比例: {(TAKE_PROFIT - 1):.2%}"
                   f"\n止盈价格: {_hold_price * TAKE_PROFIT}"
                   f"\n当前价格: {close_price}")

        send_mail(subject, content)
        dump_file(subject, content)


def get_bid_notify(_stock_code=STOCK_CODE, _stock_name=STOCK_NAME, _bid_price=0.0):
    """
    自选买入提醒
    :param _stock_code:
    :param _stock_name:
    :param _bid_price:
    :return:
    """
    df = pd.read_csv(f"{os.path.join(DUMP_DIR, _stock_code)}_{_stock_name}.csv")
    # 当天收盘价
    close_price = df.iloc[-1]['close']
    if close_price < _bid_price:
        # 邮件内容
        subject = f"{_stock_code}_{_stock_name} 买入提醒"
        content = (f"{_stock_code}_{_stock_name} 已低于设定的买入价格"
                   f"\n目标买入价格: {_bid_price}"
                   f"\n当前价格: {close_price}")

        send_mail(subject, content)
        dump_file(subject, content)


if __name__ == '__main__':
    login()

    # 持仓卖出
    positions = get_position()

    for hold in positions:
        hold_code = hold.get('code')
        hold_name = hold.get('name')
        hold_mkt = hold.get('market')
        hold_price = hold.get('hold_price')

        get_k_data(f"{hold_mkt}.{hold_code}", hold_name)
        get_sell_notify(f"{hold_mkt}.{hold_code}", hold_name, hold_price)

    # 自选买入
    watchlist = get_watchlist()

    for watch in watchlist:
        watch_code = watch.get('code')
        watch_name = watch.get('name')
        watch_mkt = watch.get('market')
        watch_price = watch.get('bid_price')

        get_k_data(f"{watch_mkt}.{watch_code}", watch_name)
        get_bid_notify(f"{watch_mkt}.{watch_code}", watch_name, watch_price)

    logout()
