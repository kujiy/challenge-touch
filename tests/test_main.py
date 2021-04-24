from main import start
from utils.mailer import Mailer
from helpers import *


def test_start_no_url(mocked_object):

    start()

    mocked_object.mail_mock.assert_called_once()
    mocked_object.notify_new_emails_mock.assert_called_once_with([mail_obj])
    mocked_object.create_web_driver_mock.assert_not_called()
    mocked_object.send_reply_mock.assert_not_called()
    mocked_object.line_mock.assert_not_called()

def test_start_with_url(mocked_object, mocker):
    mail_obj = MockMailObj()
    mail_obj.body = 'https://ouen-net.benesse.ne.jp/open/hato/mail/?p=9r6BTOA\n'
    mail_mock = mocker.patch.object(Mailer, 'get', return_value=[mail_obj])

    start()

    mail_mock.assert_called_once()
    mocked_object.notify_new_emails_mock.assert_called_once_with([mail_obj])
    mocked_object.create_web_driver_mock.assert_called_once()
    mocked_object.send_reply_mock.assert_called_once()
    mocked_object.line_mock.assert_called_once()
