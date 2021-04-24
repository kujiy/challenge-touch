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
        print(mail.title)
        if len(mail["attachments"]) > 0:
            early_lines = os.linesep.join(mail.body.split(os.linesep)[:8])
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
        print(mail.title)
        # https://ouen-net.benesse.ne.jp/open/message?p=9r6BTOAQ0Vt_XgjUnrJiIShDgXAT0p5SKgHSOjRy-h78P8KTBlJ7hNmE9frLt28-W8BF64olvDr7sPmhlPB1n-2fLO1_fFkGsf9KUk8P5FvqHyeaa6ohd4t53-pH_qf3&utm_source=torikumi&utm_medium=email
        m = re.findall(
            r'(https://ouen-net.benesse.ne.jp/open/(hato|message).+?)\r?\n', mail.body)
        if len(m) > 0:
            urls.append(m[0][0])
    return urls


def send_reply(driver_path, url):
    try:
        # first page
        # w = Web(driver_path, headless=True)
        w = Web(driver_path)
        sleep(3)
        w.open(url)
        sleep(3)
        if w.has_replied():
            return

        try:
            # modal version
            text = w.choose_message("messageTemplate", 1)
            w.click_element("ouenmessage__selectStamp")
            stamp = w.choose_stamp_in_modal("stampModalList")
        except:
            # flat page version
            text = w.choose_message("selectKaniComment", 1)
            stamp = w.choose_stamp_in_radio("iconImage")

        sleep(1)
        w.submit("confirm")
        sleep(2)
        # second page
        w.submit("send")
        sleep(1)
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
    mails = mailer.get(3)
    print(f"received {len(mails)} mails")

    if 1:
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
                message=f"failed: {type(e)} e {str(e)}")


def create_notify(item):

    return f"""
メッセージありがとうございます！
おへんじをおくったよ！

{item['text']}
"""


if __name__ == "__main__":
    start()
