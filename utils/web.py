import os
import random
import re

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select

from selenium.webdriver.chrome.options import Options
from time import sleep

from env import env
from utils.wisdom import get_wisdom_text


class Web:

    def __init__(self, driver_path: str, headless: bool = False):
        options = Options()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(driver_path, options=options)

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.close()

    def open(self, url):
        self.driver.get(url)
        sleep(4)

    def read_raw_html(self, html: str):
        self.driver.get("http://192.168.0.251/")
        # TODO: JS実行方法が違う
        # self.driver.executeScript("document.innerHTML = " + html);

    def has_replied(self):
        return re.match(r'.*(返信済み|送信済み).*', self.driver.page_source, re.S)
    def has_limited(self):
        return re.match(r'.*(セキュリティの制限|期限を過ぎて).*', self.driver.page_source, re.S)

    def login(self):
        if self.exists_name('usr_password'):
            self.driver.find_element_by_name('usr_name').send_keys(env.LOGIN_ID)
            self.driver.find_element_by_name('usr_password').send_keys(env.LOGIN_PW)
            if self.exists_id('loginButton'):
                self.driver.find_element_by_id('loginButton').click()
            else:
                self.driver.find_element_by_class_name('sendBtn').find_element_by_tag_name('input').click()
            sleep(3)

    def add_wisdom(self) -> None:
        for name in ('free_message', 'messageInput'):
            if self.exists_name(name):
                self.driver.find_element_by_name(name).send_keys(f"""

Today's Wisdom:

{get_wisdom_text()}""")
            sleep(1)

    def put_message(self, name: str) -> str:
        select = Select(self.driver.find_element_by_name(name))
        option_index = random.randint(0,len(select.options) - 1)
        select.select_by_index(option_index)
        sleep(1)
        # add a wisdom
        self.add_wisdom()
        return select.options[option_index].text

    def click_element(self, class_name: str) -> None:
        try:
            self.driver.find_element_by_class_name(class_name).click()
            sleep(3)
        except:
            # div > a
            self.driver.find_element_by_class_name(
                class_name).find_element_by_tag_name('a').click()

    def choose_stamp_in_modal(self, ul_class_name: str, index: int) -> str:
        ul = self.driver.find_element_by_class_name(ul_class_name)
        lis = ul.find_elements_by_tag_name("li")
        for i, li in enumerate(lis):
            if i != index:
                continue
            li.click()
            return li.get_attribute("src")

    def choose_stamp_in_radio(self, radio_name: str):
        if self.exists_id('special'): # english
            radios = self.driver.find_element_by_id('special').find_elements_by_name(radio_name)
        else:
            radios = self.driver.find_elements_by_name(radio_name)
        index = random.randint(0, len(radios) - 1)
        radio = radios[index]
        parrent = radio.find_element_by_xpath('..')
        if parrent.tag_name == 'label':
            label = parrent
            sleep(1)
            label.click()
            parrent = label.find_element_by_xpath('..')
            sleep(1)
        else:
            label = parrent.find_element_by_tag_name('label')
            label.click()
            sleep(1)
        return parrent.find_element_by_tag_name('img').get_attribute('src')

    def nested_submit(self, class_name: str):
        self.driver.find_element_by_class_name(class_name).find_element_by_tag_name('input').click()
        sleep(2)

    def submit(self, name: str):
        self.driver.find_element_by_name(name).click()
        sleep(2)

    def close(self):
        try:
            self.driver.close()
        except:
            pass

    def exists_id(self, id_name):
        try:
            self.driver.find_element_by_id(id_name)
        except NoSuchElementException:
            return False
        return True

    def exists_name(self, name):
        try:
            self.driver.find_element_by_name(name)
        except NoSuchElementException:
            return False
        return True

if __name__ == "__main__":
    w = Web()
    a = w.first_page("https://www.google.com")
    print(a)
    w.close()
