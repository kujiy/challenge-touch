import os
import re
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select

from selenium.webdriver.chrome.options import Options
from time import sleep


class Web:

    def __init__(self, driver_path: str, headless: bool = False):
        options = Options()
        if headless:
            options.add_argument('--headless')
        self.driver = webdriver.Chrome(driver_path, options=options)

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.close()

    def open(self, url):
        self.driver.get(url)
        sleep(3)

    def has_limited(self):
        return re.match(r'.*(返信済み|送信済み|セキュリティの制限|期限を過ぎて).*', self.driver.page_source, re.S)

    def login(self):
        if self.exists_name('usr_password'):
            self.driver.find_element_by_name('usr_name').send_keys(os.getenv('LOGIN_ID'))
            self.driver.find_element_by_name('usr_password').send_keys(os.getenv('LOGIN_PW'))
            if self.exists_id('loginButton'):
                self.driver.find_element_by_id('loginButton').click()
            else:
                self.driver.find_element_by_class_name('sendBtn').find_element_by_tag_name('input').click()
            sleep(3)

    def choose_message(self, name, option_index):
        select = Select(self.driver.find_element_by_name(name))
        select.select_by_index(option_index)
        sleep(1)
        return select.options[option_index].text

    def click_element(self, class_name):
        try:
            self.driver.find_element_by_class_name(class_name).click()
            sleep(3)
        except:
            # div > a
            self.driver.find_element_by_class_name(
                class_name).find_element_by_tag_name('a').click()

    def choose_stamp_in_modal(self, ul_class_name, index):
        ul = self.driver.find_element_by_class_name(ul_class_name)
        lis = ul.find_elements_by_tag_name("li")
        for i, li in enumerate(lis):
            if i != index:
                continue
            li.click()
            return li.get_attribute("src")

    def choose_stamp_in_radio(self, radio_name, index):
        # TODO: choose Nth radio
        radio = self.driver.find_element_by_name(radio_name)
        parrent = radio.find_element_by_xpath('..')
        if parrent.tag_name == 'label':
            label = parrent
            label.click()
            parrent = label.find_element_by_xpath('..')
            sleep(1)
        else:
            label = parrent.find_element_by_tag_name('label')
            label.click()
            sleep(1)
        return parrent.find_element_by_tag_name('img').get_attribute('src')

    def click_class_input(self, class_name):
        self.driver.find_element_by_class_name(class_name).find_element_by_tag_name('input').click()
        sleep(2)

    def submit(self, name):
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
    try:
        w = Web()
        a = w.first_page("https://www.google.com")
        print(a)
        w.close()
    except:
        w.close()
        raise
