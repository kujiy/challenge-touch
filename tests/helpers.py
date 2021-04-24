import json
from unittest.mock import Mock
from requests.models import Response
from main import start
from utils.line import Line
from utils.mailer import Mailer
import pytest

class MockMailObj:
    title = 'test'
    body = 'test'
    attachments = []

class MockWebDriver:
    def close(self):
        pass

line_response = Mock(spec=Response)
line_response.json.return_value = {'status': 'ok'}
line_response.status_code = 200

mail_obj = MockMailObj()

@pytest.fixture(autouse=True)
def mocked_object(mocker):
    class MockObject(object):
        mail_mock = mocker.patch.object(Mailer, 'get', return_value=[mail_obj])
        notify_new_emails_mock = mocker.patch('main.notify_new_emails', return_value=True)
        send_reply_mock = mocker.patch('main.send_reply', return_value={'text':'sent','stamp':'stamp'})
        line_mock = mocker.patch('utils.line.requests.post', return_value=line_response)
        retrieve_byte_image_mock = mocker.patch.object(Line, 'retrieve_byte_image', return_value=b'abc')
        create_web_driver_mock = mocker.patch('main.create_web_driver', return_value=MockWebDriver())
    return MockObject()

