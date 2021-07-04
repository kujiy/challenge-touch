import datetime
import json
import os
import sys
import re
import traceback
import base64
import random
from time import sleep
from typing import Optional

import selenium
from pydantic import BaseModel

from utils.web import Web
from utils.line import Line
from utils.mailer import Mailer
from utils.logger import logger
from dotenv import load_dotenv
load_dotenv()

class Challenge:
    def __init__(self):
        self.mailer = Mailer(
            host=os.getenv("MAIL_HOST", 'test'),
            user=os.getenv("MAIL_USER", 'test'),
            pw=os.getenv("MAIL_PASSWORD", 'test'),
            mailbox=os.getenv("MAIL_BOX", 'test')
        )
        self.line = Line(token=os.getenv("LINE_TOKEN", 'test'))


def notify_new_emails(mails):
    for mail in mails:
        logger.info(mail.title)
        if len(mail.attachments) > 0:
            early_lines = os.linesep.join(mail.body.split(os.linesep)[:8])
            res = c.line.post(message=early_lines)
            logger.info(res)
            for attachment in mail.attachments:
                # attachment = (filename, data, content_type)
                res = c.line.post_raw_image(
                    message=attachment[0], raw_image=attachment[1])
                # logger.info(res)


def extract_ouen_urls(mails):
    urls = []
    for mail in mails:
        logger.info(mail.title)
        # https://ouen-net.benesse.ne.jp/open/message?p=9r6BTOAQ0Vt_XgjUnrJiIShDgXAT0p5SKgHSOjRy-h78P8KTBlJ7hNmE9frLt28-W8BF64olvDr7sPmhlPB1n-2fLO1_fFkGsf9KUk8P5FvqHyeaa6ohd4t53-pH_qf3&utm_source=torikumi&utm_medium=email
        m = re.search(
            r'(?P<url>https://ouen-net.benesse.ne.jp/open/(?P<_type>hato|message).+?)[\'"]', mail.body)
        e = re.search(
            r'(?P<url>https://mail-t.benesse.ne.jp/.+?\?.+?)[\'"]', mail.body)
        g = re.search(
            r'(?P<url>https://ce.benesse.ne.jp/member/Goodjob.*?)[\'"]', mail.body)
        if m and "url" in m.groupdict():
            urls.append(m.group('url'))
        if e and "url" in e.groupdict():
            urls.append(e.group('url'))
        if g and "url" in g.groupdict():
            urls.append(g.group('url'))

    return urls

class ReplyModel(BaseModel):
    text: str
    stamp: Optional[str]

def send_reply(c: Challenge, w: Web, url: str) -> Optional[ReplyModel]:
    try:
        # first page
        w.open(url)
        w.login()
        if w.has_limited():
            logger.info('already replied.')
            return

        if w.exists_id('GoodjobIndex'):
            # challeng english - https://ce.benesse.ne.jp/member/Goodjob
            text = w.choose_message("template_id", random.randint(1,8))
            stamp = w.choose_stamp_in_radio("stamp_id", random.randint(1,4))
            # open the confirm page
            w.click_class_input('bottomBtn')
            # submit on the confirm page
            w.click_class_input('bottomBtn')
        else:
            # challenge touch
            if w.exists_name('open_messageActionForm'):
                # modal version
                text = w.choose_message("messageTemplate", random.randint(1,4))
                w.click_element("ouenmessage__selectStamp")
                stamp = w.choose_stamp_in_modal("stampModalList", random.randint(1,4))
            else:
                # flat page version
                text = w.choose_message("selectKaniComment", random.randint(1,4))
                stamp = w.choose_stamp_in_radio("iconImage", random.randint(1,4))

            w.submit("confirm")
            # second page
            w.submit("send")

        return ReplyModel(text=text, stamp=stamp)
    except selenium.common.exceptions.NoSuchElementException as e:
        logger.error(sys.exc_info(), traceback.extract_stack())


def create_web_driver(driver_path: str, headless: bool = False) -> Web:
    return Web(driver_path, headless=headless)

def notify_fail(c: Challenge, e: Exception):
    c.line.post(message=f"failed: {type(e)} e {str(e)} {json.dumps(c)} {sys.exc_info()} {traceback.extract_stack()}")

def start():
    c = Challenge()

    try:
        # retrieve emails
        mails = c.mailer.get(10)
        logger.info(f"--- received {len(mails)} mails  --------------- {datetime.datetime.now()}")

        if os.environ.get('NO_NEWMAIL_NOTIFY') != 'True': # debug
            try:
                notify_new_emails(mails)
            except Exception as e:
                logger.error(
                    f"notify new email failed: {type(e)} e {str(e)}\n{traceback.print_exc()}")

        # urls = ["https://ouen-net.benesse.ne.jp/open/message/?p=9r6BTOAQ0Vt_XgjUnrJiIb5uFMVsVr3JiW-lYBlJZc3Okk-eoTmnrHuMvzNBXK3QDjvqbiQfLFgBMZVE0JFR5yM09jNMTmtWn1GlcXBsrBoaMZ-9z-0MosSBLSL_KkNX&utm_source=torikumi&utm_medium=email"]
        urls = extract_ouen_urls(mails)
        # urls = ['https://ce.benesse.ne.jp/member/Goodjob']
        # urls = ['https://ouen-net.benesse.ne.jp/open/message/?p=9r6BTOAQ0Vt_XgjUnrJiIbP1IxzjarCLsVz6zPgNMqZZaZg074zmkXvBhvmGYaSWYhHdMwBB_MzWYmNh9vEiTwychnUE6mPcSELfjCAtOtRgrjWaPbd0JmevMWQw2RFo&utm_source=torikumi&utm_medium=email']
        logger.info(f" found {len(urls)} urls")

        if len(urls) == 0:
            return

        headless = False if os.getenv('CHROME_DRIVER_HEADLESS', None) == 'False' else True
        w: Web = create_web_driver(os.getenv('CHROME_DRIVER_PATH'), headless=headless)
        # w = Web(os.getenv('CHROME_DRIVER_PATH'))
        sleep(3)

        for url in urls:
            logger.info(url)
            choosen_items: ReplyModel = send_reply(c, w, url)
            if choosen_items:
                message = create_notify(choosen_items)
                res = c.line.post_image_by_url(
                    message=message, image_url=choosen_items.stamp)
                logger.info(res)
    except Exception as e:
        notify_fail(c, e)
    finally:
        w.close()

def create_notify(item: ReplyModel) -> str:

    return f"""
メッセージありがとうございます！
おへんじをおくったよ！

{item.text}
"""


if __name__ == "__main__":
    start()
