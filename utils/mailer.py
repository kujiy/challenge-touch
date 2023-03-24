from utils.easyimap import *
import email.utils
import datetime


class Mailer():

    def __init__(self, *args, **kwargs):
        self.connect(**kwargs)

    def connect(self, **kwargs):
        self.imapper = connect(
            kwargs.get("host"),
            kwargs.get("user"),
            kwargs.get("pw"),
            kwargs.get("mailbox"),
            kwargs.get("timeout", 15),
            kwargs.get("ssl", True),
            kwargs.get("port", 993),
        )

    def get(self, limit):
        mails = self.imapper.unseen(999, include_raw=True)
        return self.order_by_date_asc(mails)

    # because imap does not support sort officially.
    def order_by_date_asc(self, mails):
        return sorted(mails, key=lambda k: k.date)

    def _parse_date(self, date_str):

        date_tuple = email.utils.parsedate_tz(date_str)
        if date_tuple:
            date = datetime.datetime.fromtimestamp(
                email.utils.mktime_tz(date_tuple))
            f = '%Y-%m-%d %H:%M:%S'
            return date.strftime(f)
        return ""

    def extract_mail_loop(self, mails):
        out = []
        for mail in mails:
            out.append(self.extract_mail(mail))
        return out

    # dict形式
    def extract_mail(self, m):
        return {
            "date": self._parse_date(m.date),
            "from_addr": m.from_addr,
            "cc_addr": m.cc,
            "subject": m.title,
            "to_addr": m.to,
            "message_id": m.message_id,
            "body": m.body,
            "in_reply_to": m.in_reply_to,
            "reply_to": m.reply_to,
            "attachments": m.attachments
        }

    def quit(self):
        self.imapper.quit()
