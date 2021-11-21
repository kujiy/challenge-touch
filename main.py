import datetime
import os
import sys
import re
import time
import traceback
import base64
import random
from time import sleep
from typing import Optional, List

import selenium
from pydantic import BaseModel

from env import env
from utils.web import Web
from utils.line import Line
from utils.easyimap import MailObj
from utils.mailer import Mailer
from utils.logger import logger


class NoFormError(Exception):
    pass


class ExpiredError(Exception):
    pass


class AlreadyRepliedError(Exception):
    pass


g_line = Line(token=env.LINE_TOKEN)


class Challenge:
    def __init__(self):
        self.mailer = Mailer(
            host=env.MAIL_HOST,
            user=env.MAIL_USER,
            pw=env.MAIL_PASSWORD,
            mailbox=env.MAIL_BOX,
        )
        self.line = Line(token=env.LINE_TOKEN)


def notify_new_emails(mails: list, c: Challenge):
    mail: MailObj
    for mail in mails:
        logger.info(mail.title)
        if len(mail.attachments) > 0:
            early_lines = os.linesep.join(mail.body.split(os.linesep)[:8])
            res = c.line.post(message=early_lines)
            logger.info(res)
            for attachment in mail.attachments:
                res = c.line.post_raw_image(
                    message=attachment[0], raw_image=attachment[1])
                # logger.info(res)


class ExtractedEmail(BaseModel):
    title: str
    url: str


def extract_ouen_urls(mails) -> List[ExtractedEmail]:
    extracted_email = []
    for mail in mails:
        logger.info(mail.title)
        # https://ouen-net.benesse.ne.jp/open/message?p=9r6BTOAQ0Vt_XgjUnrJiIShDgXAT0p5SKgHSOjRy-h78P8KTBlJ7hNmE9frLt28-W8BF64olvDr7sPmhlPB1n-2fLO1_fFkGsf9KUk8P5FvqHyeaa6ohd4t53-pH_qf3&utm_source=torikumi&utm_medium=email
        m = re.search(
            r'(?P<url>https://ouen-net.benesse.ne.jp/open/(?P<_type>hato|message).+?)[\'"\n]', mail.body)
        e = re.search(
            r'(?P<url>https://mail-t.benesse.ne.jp/.+?\?.+?)[\'"\n]', mail.body)
        g = re.search(
            r'(?P<url>https://ce.benesse.ne.jp/member/Goodjob.*?)[\'"\n]', mail.body)
        if m and "url" in m.groupdict():
            extracted_email.append(ExtractedEmail(title=mail.title, url=m.group('url')))
        if e and "url" in e.groupdict():
            extracted_email.append(ExtractedEmail(title=mail.title, url=e.group('url')))
        if g and "url" in g.groupdict():
            extracted_email.append(ExtractedEmail(title=mail.title, url=g.group('url')))

    return extracted_email


class ReplyModel(BaseModel):
    text: str
    stamp: Optional[str]


def send_reply(w: Web, extracted_email: ExtractedEmail) -> Optional[ReplyModel]:
    url: str = extracted_email.url
    try:
        # first page
        w.open(url)
        w.login()
        if w.has_limited():
            logger.info('already expired.')
            return
        if w.has_replied():
            logger.info('already replied.')
            return

        if w.exists_id('GoodjobIndex'):
            # challeng english - https://ce.benesse.ne.jp/member/Goodjob
            text = w.put_message("template_id")
            stamp = w.choose_stamp_in_radio("stamp_id")
            # open the confirm page
            w.nested_submit('bottomBtn')
            # submit on the confirm page
            w.nested_submit('bottomBtn')
        else:
            # challenge touch
            if w.exists_name('open_messageActionForm'):
                logger.info("mode=[open_messageActionForm]")
                # modal version
                text = w.put_message("messageTemplate")
                w.click_element("ouenmessage__selectStamp")
                stamp = w.choose_stamp_in_modal("stampModalList", random.randint(1, 4))
            elif w.exists_name("selectKaniComment"):
                # flat page version / hato
                text = w.put_message("selectKaniComment")
                stamp = w.choose_stamp_in_radio("iconImage")
            else:
                # no form exists OR a new form is found.
                raise NoFormError(f'no form exists OR a new form is found on {url}')

            time.sleep(5)
            w.submit("confirm")
            # second page
            w.submit("send")

        return ReplyModel(text=text, stamp=stamp)
    except selenium.common.exceptions.NoSuchElementException as e:
        logger.error(extracted_email.title, sys.exc_info(), traceback.extract_stack())


def create_web_driver(headless: bool = False) -> Web:
    return Web(env.CHROME_DRIVER_PATH, headless=headless)


def notify_fail(c: Challenge, e: Exception):
    c.line.post(message=f"failed: [{type(e)}] {str(e)} {sys.exc_info()} {traceback.extract_stack()}")


def print_and_line(msg):
    logger.info(msg)
    g_line.post(message=msg)


def start():
    try:
        create_web_driver(env.CHROME_DRIVER_HEADLESS)
    except selenium.common.exceptions.SessionNotCreatedException as e:
        print_and_line(f"""[ChromeWebDriverVersionError]
        path= {env.CHROME_DRIVER_PATH}
        url= https://chromedriver.chromium.org/downloads
         {e}""")
        sys.exit(1)

    c = Challenge()
    try:

        # retrieve emails
        mails: list = c.mailer.get(10)
        logger.info(f"--- received {len(mails)} mails  --------------- {datetime.datetime.now()}")

        if env.NEWMAIL_NOTIFY:  # set False when debug
            try:
                notify_new_emails(mails, c)
            except Exception as e:
                logger.error(
                    f"notify new email failed: {type(e)} e {str(e)}\n{traceback.print_exc()}")

        extracted_emails: List[ExtractedEmail] = extract_ouen_urls(mails)
        # extracted_emails = ['https://ouen-net.benesse.ne.jp/open/message/?p=9r6BTOAQ0Vt_XgjUnrJiIbP1IxzjarCLsVz6zPgNMqZZaZg074zmkXvBhvmGYaSWYhHdMwBB_MzWYmNh9vEiTwychnUE6mPcSELfjCAtOtRgrjWaPbd0JmevMWQw2RFo&utm_source=torikumi&utm_medium=email']
        # extracted_emails = ['https://ce.benesse.ne.jp/member/Goodjob'] # english
        # extracted_emails = ['https://ouen-net.benesse.ne.jp/open/hato/mail?p=9r6BTOAQ0Vt_XgjUnrJiIR122DwoYp2ciFDXUanjxr7DpubrQJHirUWcP5SdJvIqPIcv27pTvrrE9H_W6ZlALw'] # hato
        logger.info(f" found {len(extracted_emails)} extracted_emails")

        if len(extracted_emails) == 0:
            return

        with create_web_driver(env.CHROME_DRIVER_HEADLESS) as w:
            sleep(3)

            for mailset in extracted_emails:
                logger.info(mailset)
                try:
                    choosen_items: Optional[ReplyModel] = send_reply(w, mailset)
                except NoFormError as e:
                    notify_fail(c, e)
                    continue

                if choosen_items is None:
                    continue

                logger.info('[success] proccessed.')
                message: str = create_notify(choosen_items)
                res: dict = c.line.post_image_by_url(
                    message=message, image_url=choosen_items.stamp)
                logger.info(res)
    except Exception as e:
        notify_fail(c, e)
        raise


def create_notify(item: ReplyModel) -> str:
    return f"""
メッセージありがとうございます！
おへんじをおくったよ！

{item.text}
"""


if __name__ == "__main__":
    start()
    logger.info('[Done]')