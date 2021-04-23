from utils.easyimap import *
import email.utils
import datetime

class Mailer():

    def __init__(self, **kargs):
        self.imapper = connect(
            kargs.get("host"),
            kargs.get("user"),
            kargs.get("pw"),
            kargs.get("mailbox"),
            kargs.get("timeout", 15),
            kargs.get("ssl", True),
            kargs.get("port", 993),
        )

    def receive(self, limit=10):
        return self.imapper.unseen(limit, include_raw=True)

    def get(self, limit):
        mails = self.receive(limit)
        dict_mails = self.extract_mail_loop(mails)
        return self.order_by_date_asc(dict_mails)

    # because imap does not support sort officially.
    def order_by_date_asc(self, mails):
        return sorted(mails, key=lambda k: k['date'])

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
