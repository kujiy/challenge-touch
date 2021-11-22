from pydantic import BaseSettings


class Env(BaseSettings):
    CHROME_DRIVER_HEADLESS: bool = True
    CHROME_DRIVER_PATH: str = 'test'

    LINE_TOKEN: str = 'test'

    MAIL_HOST: str = 'test'
    MAIL_USER: str = 'test'
    MAIL_PASSWORD: str = 'test'
    MAIL_BOX: str = 'test'

    # challenge login
    LOGIN_ID: str # '1405xxxxx'
    LOGIN_PW: str

    # set False when debug
    NEWMAIL_NOTIFY: bool = True

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


env = Env()