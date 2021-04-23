import os
import sys
import re
import traceback
import base64
from time import sleep

import selenium

from utils.web import Web
from utils.line import Line
from utils.mailer import Mailer
from dotenv import load_dotenv
load_dotenv()

mailer = Mailer(
    host=os.getenv("MAIL_HOST"),
    user=os.getenv("MAIL_USER"),
    pw=os.getenv("MAIL_PASSWORD"),
    mailbox=os.getenv("MAIL_BOX")
)
line = Line(token=os.getenv("LINE_TOKEN"))


def notify_new_emails(mails):
    for mail in mails:
        print(mail["subject"])
        if len(mail["attachments"]) > 0:
            early_lines = os.linesep.join(mail['body'].split(os.linesep)[:8])
            res = line.post(message=early_lines)
            print(res)
            for attachment in mail["attachments"]:
                # attachment = (filename, data, content_type)
                res = line.post_raw_image(
                    message=attachment[0], raw_image=attachment[1])
                # print(res)


def extract_ouen_urls(mails):
    urls = []
    for mail in mails:
        print(mail["subject"])
        m = re.findall(
            r'(https://ouen-net.benesse.ne.jp/open/hato/mail?.+?)\r?\n', mail['body'])
        if len(m) > 0:
            urls += m
    return urls


def send_reply(driver_path, url):
    try:
        # first page
        w = Web(driver_path, headless=True)
        w.open(url)
        sleep(2)
        text = w.choose_message("messageTemplate", 1)
        w.click_element("ouenmessage__selectStamp")
        sleep(2)
        stamp = w.choose_stamp("stampModalList")
        w.submit("confirm")

        # second page
        w.submit("send")

        w.close()

        return {"text": text, "stamp": stamp}
    except selenium.common.exceptions.NoSuchElementException:
        pass
    except:
        w.close()
        res = line.post(message=f"challenge failed: {url}")
        print(res)
        raise


def start():
    # retrieve emails
    mails = mailer.get(10)
    print(f"received {len(mails)} mails")

    try:
        notify_new_emails(mails)
    except Exception as e:
        print(
            f"notify new email failed: {type(e)} e {str(e)}\n{traceback.print_exc()}")

    urls = extract_ouen_urls(mails)

    print(f"found {len(urls)} urls")
    # urls = ["https://ouen-net.benesse.ne.jp/open/message/?p=9r6BTOAQ0Vt_XgjUnrJiIb5uFMVsVr3JiW-lYBlJZc3Okk-eoTmnrHuMvzNBXK3QDjvqbiQfLFgBMZVE0JFR5yM09jNMTmtWn1GlcXBsrBoaMZ-9z-0MosSBLSL_KkNX&utm_source=torikumi&utm_medium=email"]
    for url in urls:
        try:
            print(url)
            choosen_items = send_reply(os.getenv('CHROME_DRIVER_PATH'), url)
            if choosen_items is not None:
                message = create_notify(choosen_items)
                res = line.post_image_by_url(
                    message=message, image_url=choosen_items['stamp'])
                print(res)
        except Exception as e:
            line.post(
                message=f"failed: {type(e)} e {str(e)}\n{traceback.print_exc()}")


def create_notify(item):

    return f"""
メッセージありがとうございます！
おへんじをおくったよ！

{item['text']}
"""


if __name__ == "__main__":
    start()
