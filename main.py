import datetime
import os
import sys
import re
import traceback
import base64
import random
from time import sleep

import selenium

from utils.web import Web
from utils.line import Line
from utils.mailer import Mailer
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
        print(mail.title)
        if len(mail.attachments) > 0:
            early_lines = os.linesep.join(mail.body.split(os.linesep)[:8])
            res = c.line.post(message=early_lines)
            print(res)
            for attachment in mail.attachments:
                # attachment = (filename, data, content_type)
                res = c.line.post_raw_image(
                    message=attachment[0], raw_image=attachment[1])
                # print(res)


def extract_ouen_urls(mails):
    urls = []
    for mail in mails:
        print(mail.title)
        # https://ouen-net.benesse.ne.jp/open/message?p=9r6BTOAQ0Vt_XgjUnrJiIShDgXAT0p5SKgHSOjRy-h78P8KTBlJ7hNmE9frLt28-W8BF64olvDr7sPmhlPB1n-2fLO1_fFkGsf9KUk8P5FvqHyeaa6ohd4t53-pH_qf3&utm_source=torikumi&utm_medium=email
        m = re.findall(
            r'(https://ouen-net.benesse.ne.jp/open/(hato|message).+?)\r?\n', mail.body)
        if len(m) > 0:
            urls.append(m[0][0])
    return urls


def send_reply(w, url):
    try:
        # first page
        w.open(url)
        sleep(3)
        if w.has_limited():
            print('already replied.')
            return

        try:
            # modal version
            text = w.choose_message("messageTemplate", random.randint(1,4))
            w.click_element("ouenmessage__selectStamp")
            stamp = w.choose_stamp_in_modal("stampModalList", random.randint(1,4))
        except:
            # flat page version
            text = w.choose_message("selectKaniComment", random.randint(1,4))
            stamp = w.choose_stamp_in_radio("iconImage", random.randint(1,4))

        sleep(1)
        w.submit("confirm")
        sleep(2)
        # second page
        w.submit("send")
        sleep(1)

        return {"text": text, "stamp": stamp}
    except selenium.common.exceptions.NoSuchElementException:
        pass
    except:
        res = c.line.post(message=f"challenge failed: {url}")
        print(res)
        raise


def create_web_driver(driver_path, headless=False):
    return Web(driver_path, headless=headless)

def notify_fail(c, e):
    c.line.post(message=f"failed: {type(e)} e {str(e)}")

def start():
    c = Challenge()

    try:
        # retrieve emails
        mails = c.mailer.get(10)
        print(f"--- received {len(mails)} mails  --------------- {datetime.datetime.now()}")

        if os.environ.get('NO_NEWMAIL_NOTIFY') != 'True': # debug
            try:
                notify_new_emails(mails)
            except Exception as e:
                print(
                    f"notify new email failed: {type(e)} e {str(e)}\n{traceback.print_exc()}")

        # urls = ["https://ouen-net.benesse.ne.jp/open/message/?p=9r6BTOAQ0Vt_XgjUnrJiIb5uFMVsVr3JiW-lYBlJZc3Okk-eoTmnrHuMvzNBXK3QDjvqbiQfLFgBMZVE0JFR5yM09jNMTmtWn1GlcXBsrBoaMZ-9z-0MosSBLSL_KkNX&utm_source=torikumi&utm_medium=email"]
        urls = extract_ouen_urls(mails)
        print(f" found {len(urls)} urls")

        if len(urls) == 0:
            return

        w = create_web_driver(os.getenv('CHROME_DRIVER_PATH'), headless=True)
        # w = Web(os.getenv('CHROME_DRIVER_PATH'))
        sleep(3)

        for url in urls:
            try:
                print(url)
                choosen_items = send_reply(w, url)
                if choosen_items is not None:
                    message = create_notify(choosen_items)
                    res = c.line.post_image_by_url(
                        message=message, image_url=choosen_items['stamp'])
                    print(res)
            except Exception as e:
                notify_fail(c, w, e)
        w.close()
    except Exception as e:
        notify_fail(c, e)
        try:
            w.close()
        except:
            pass
        raise e

def create_notify(item):

    return f"""
メッセージありがとうございます！
おへんじをおくったよ！

{item['text']}
"""


if __name__ == "__main__":
    start()
