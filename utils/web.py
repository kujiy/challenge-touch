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

    def choose_message(self, name, option_index):
        select = Select(self.driver.find_element_by_name(name))
        select.select_by_index(option_index)
        return select.options[option_index].text

    def click_element(self, class_name):
        self.driver.find_element_by_class_name(class_name).click()

    def choose_stamp(self, ul_class_name):
        ul = self.driver.find_element_by_class_name(ul_class_name)
        lis = ul.find_elements_by_tag_name("li")
        for li in lis:
            li.click()
            return li.get_attribute("src")

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
