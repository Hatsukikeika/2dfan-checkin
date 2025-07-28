import json
import os

os.environ["PYPPETEER_CHROMIUM_REVISION"] = '1181217'

import sys
import asyncio
import time
import logging
from api import User
from recaptcha import EzCaptchaImpl
from logging.handlers import RotatingFileHandler
from datetime import datetime

CONFIG_FILE = "config.json"

SESSION_MAP = [""]

http_proxy: str = os.environ.get(key='HTTP_PROXY', default=None)

signed = False

async def main():
    logging.info("开始签到...")
    global signed 
    for key in SESSION_MAP[0].keys():
        try:
            session = SESSION_MAP[0][key]
            user = User(session["id"], session["auth"], EzCaptchaImpl())
            if http_proxy:
                user.session.proxies.update({
                    'http': http_proxy,
                    'https': http_proxy,
                })
            result = await user.checkin()
            logging.info(f"session: {key} 签到结果: {result.__dict__}")
            signed = True
        except Exception as exception:
            logging.error(f"签到失败: {str(exception)}")
    logging.info("签到结束")

def logger_setup():
    try:
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        file_handler = RotatingFileHandler(
            filename="2df-signin.log",
            maxBytes=10*1024*1024,
            backupCount=5,
            encoding='utf-8'
        )

        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        logging.info("日志系统初始化成功")
        return logger

    except Exception as e:
        print(f"日志系统初始化失败: {str(e)}")
        sys.exit(1)

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
            if config.get("sessions") and config.get("ez_captcha"):
                SESSION_MAP[0] = config.get("sessions")
                os.environ["EZCAPTCHA_CLIENT_KEY"] = config.get("ez_captcha")
                logging.info("加载登入信息成功！")
            else:
                logging.error("加载登入信息失败")
                logging.info(f"退出...")
                sys.exit(1)
        except Exception as e:
            logging.error(f"加载登入信息失败: {str(e)}")
            logging.info(f"退出...")
            sys.exit(1)
    else:
        logging.info("配置文件不存在， 无法加载登入信息。")
        logging.info(f"退出...")
        sys.exit(1)

if __name__ == '__main__': 
    logger_setup()
    load_config()

    while True:
        logging.info("检查当前时间....")
        logging.info(f"当前时间: {datetime.now().hour} 时 {datetime.now().minute} 分, 已签到: {signed}")
        if signed == False and datetime.now().hour >= 15:
            asyncio.run(main())
        elif datetime.now().hour < 15:
            signed = False
        time.sleep(60 * 60)
