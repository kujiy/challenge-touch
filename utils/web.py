import re
from selenium import webdriver
from selenium.webdriver.support.ui import Select

from selenium.webdriver.chrome.options import Options

class Web:

    def __init__(self, driver_path, headless=False):
        options = Options()
        if headless:
            options.add_argument('--headless')
        self.driver = webdriver.Chrome(driver_path, options=options)

    def open(self, url):
        self.driver.get(url)

    def has_limited(self):
        return re.match(r'.*(返信済み|送信済み|セキュリティの制限).*', self.driver.page_source, re.S)

    def choose_message(self, name, option_index):
        select = Select(self.driver.find_element_by_name(name))
        select.select_by_index(option_index)
        return select.options[option_index].text

    def click_element(self, class_name):
        self.driver.find_element_by_class_name(class_name).click()

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
        label = parrent.find_element_by_tag_name('label')
        label.click()
        return parrent.find_element_by_tag_name('img').get_attribute('src')

    def submit(self, name):
        self.driver.find_element_by_name(name).click()

    def close(self):
        try:
            self.driver.close()
        except:
            pass


if __name__ == "__main__":
    try:
        w = Web()
        a = w.first_page("https://www.google.com")
        print(a)
        w.close()
    except:
        w.close()
        raise
