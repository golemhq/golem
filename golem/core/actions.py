import selenium
from golem import core

from golem.core.utils import get_selenium_object

def click(obj):
    #if context.engine=='selenium':
    driver = core.getOrCreateWebdriver()
    test_object = get_selenium_object(obj, driver)
    #log clicking
    test_object.click()
        
    
def goto(url):
    #if self.context.engine=='selenium':
    driver = core.getOrCreateWebdriver()
    driver.get(url)


def fill(obj, text):
    #if self.context.engine == 'selenium':
    driver = core.getOrCreateWebdriver()
    test_object = get_selenium_object(obj, driver)
    test_object.send_keys(text)
    
        
def close():
    #if self.context.engine=='selenium':
    driver = core.getOrCreateWebdriver()
    driver.quit()