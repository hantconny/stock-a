# -*- coding:utf-8 -*-
import os.path
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr

from loguru import logger

from settings import QQ_EMAIL, QQ_SMTP_SERVER, QQ_SMTP_PORT, QQ_AUTH_CODE


def send_mail(subject="", content=""):
    """
    发送邮件提醒
    :param subject:
    :param content:
    :return:
    """
    # 构建 MIME 邮件对象
    msg = MIMEText(content, "plain", "utf-8")
    msg["From"] = formataddr((str(Header("自己", "utf-8")), QQ_EMAIL))
    msg["To"] = formataddr((str(Header("自己", "utf-8")), QQ_EMAIL))
    msg["Subject"] = Header(subject, "utf-8")

    # 发送邮件
    try:
        server = smtplib.SMTP_SSL(QQ_SMTP_SERVER, QQ_SMTP_PORT)
        server.login(QQ_EMAIL, QQ_AUTH_CODE)
        server.sendmail(QQ_EMAIL, [QQ_EMAIL], msg.as_string())
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
    filepath = os.path.join(r"C:/Users/Administrator/Desktop", f"{title}.text")

    try:
        with open(filepath, encoding='utf-8', mode='w') as f:
            f.write(content)
            logger.info("文件提醒生成成功！")
    except Exception as e:
        logger.error("文件提醒生成失败：", e)
