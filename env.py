from pydantic import BaseSettings


class Env(BaseSettings):
    CHROME_DRIVER_HEADLESS: bool = True
    CHROME_DRIVER_PATH: str = 'test'

    LINE_TOKEN: str = 'test'

    MAIL_HOST: str = 'test'
    MAIL_USER: str = 'test'
    MAIL_PASSWORD: str = 'test'
    MAIL_BOX: str = 'test'

    NO_NEWMAIL_NOTIFY: bool

env = Env()