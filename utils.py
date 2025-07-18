# -*- coding:utf-8 -*-
import os.path
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr
from pathlib import Path

from loguru import logger

from settings import QQ_EMAIL, QQ_SMTP_SERVER, QQ_SMTP_PORT, QQ_AUTH_CODE, DUMP_DIR, ENABLE_MAIL_NOTIFY, \
    ENABLE_FILE_NOTIFY, SAVE_DATA, ICLOUD_EMAIL


def send_mail(subject="", content=""):
    """
    发送邮件提醒
    :param subject:
    :param content:
    :return:
    """
    if not ENABLE_MAIL_NOTIFY:
        logger.warning("邮件提醒未启用！")
        return

    # 构建 MIME 邮件对象
    msg = MIMEText(content, "plain", "utf-8")
    msg["From"] = formataddr((str(Header("自己", "utf-8")), QQ_EMAIL))
    msg["To"] = formataddr((str(Header("自己", "utf-8")), ICLOUD_EMAIL))
    msg["Subject"] = Header(subject, "utf-8")

    # 发送邮件
    try:
        server = smtplib.SMTP_SSL(QQ_SMTP_SERVER, QQ_SMTP_PORT)
        server.login(QQ_EMAIL, QQ_AUTH_CODE)
        server.sendmail(QQ_EMAIL, [ICLOUD_EMAIL], msg.as_string())
        server.quit()
        logger.info("邮件发送成功！")
    except Exception as e:
        logger.error("邮件发送失败：", e)


def dump_file(title="", content=""):
    """
    生成桌面警示文件
    :param title:
    :param content:
    :return:
    """
    if not ENABLE_FILE_NOTIFY:
        logger.warning("文件提醒未启用！")
        return

    filepath = os.path.join(r"C:/Users/Administrator/Desktop", f"{title}.text")

    try:
        with open(filepath, encoding='utf-8', mode='w') as f:
            f.write(content)
            logger.info("文件提醒生成成功！")
    except Exception as e:
        logger.error("文件提醒生成失败：", e)


def clear_file():
    """
    清空 DUMP_DIR 目录下的 csv 文件和 log 文件
    :return:
    """
    # 如果需要留存数据，则不清理 csv 文件
    if SAVE_DATA:
        return

    dump_dir = Path(DUMP_DIR)

    for f in dump_dir.glob('*.csv'):
        f.unlink()

    # for f in dump_dir.glob('*.log'):
    #     f.unlink()
