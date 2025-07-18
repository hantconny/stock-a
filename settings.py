# -*- coding:utf-8 -*-
import os
import time

DUMP_DIR = '/home/rhino/s/a'
if not os.path.exists(DUMP_DIR):
    os.makedirs(DUMP_DIR)

# 2025-07-17
TODAY = time.strftime('%Y-%m-%d', time.localtime())

# 是否生成图表
PLOT = False

# 是否留存数据
SAVE_DATA = False

# 2001年科技股泡沫破裂&国有股坚持
# 2008年次贷危机：
# 2015年杠杆股灾
# 2018年贸易战&去杠杆
# 2020年疫情
# 2022年地产债务&外资流出
CRASHES = [
    ("2001-06-01", "2005-07-01"),
    ("2007-10-01", "2008-11-01"),
    ("2015-06-01", "2015-10-01"),
    ("2018-01-01", "2019-01-01"),
    ("2020-01-01", "2020-04-01"),
    ("2022-02-01", "2022-12-01"),
]

# 回溯开始时间
START_DATE = "2018-01-01"

# 证券代码
STOCK_CODE = "sz.002475"
STOCK_NAME = "立讯精密"

# 目标买入价
BID_PRICE = 35.36

# 上涨 20% 卖出
TAKE_PROFIT = 1.2

# 是否启用文件提醒
ENABLE_FILE_NOTIFY = False

# 是否启用邮件提醒
ENABLE_MAIL_NOTIFY = True
# QQ 邮箱的 SMTP 服务器地址
QQ_SMTP_SERVER = "smtp.qq.com"
# QQ 邮箱的 SMTP 服务器端口
QQ_SMTP_PORT = 465
# QQ 邮箱，正式部署需要切换成专用的 QQ 邮箱
QQ_EMAIL = "405762304@qq.com"
# QQ 邮箱授权码，正式部署需要切换成专用 QQ 邮箱的授权码
QQ_AUTH_CODE = "dcfunepdqfgjbggh"

# 收信邮箱
ICLOUD_EMAIL = "caizheng.x@icloud.com"