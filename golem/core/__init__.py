import sys
import os

from selenium import webdriver

# values used during the execution of a test case
driver = None
driver_name = None
settings = None
project = None
workspace = None
test_data = None
report_directory = None


def get_or_create_webdriver(*args):
    global settings
    global driver

    if not driver:
        driver_selected = get_selected_driver()
        if driver_selected == 'firefox':
            if 'gecko_driver_path' in settings:
                #os.environ["webdriver.firefox.driver"] = settings['gecko_driver_path']
                os.environ["webdriver.gecko.driver"] = settings['gecko_driver_path']
                driver = webdriver.Firefox()
            else:
                sys.exit('Error: gecko_driver_path setting is not defined')
        if driver_selected == 'chrome':
            if 'chrome_driver_path' in settings:
                driver = webdriver.Chrome(executable_path=settings['chrome_driver_path'])
            else:
                sys.exit('Error: chrome_driver_path setting is not defined')
        # if driver_selected == 'ie':
        #     driver = webdriver.Ie()
        # if driver_selected == 'phantomjs':
        #     if os.name == 'nt':
        #         executable_path = os.path.join(
        #                                     golem.__path__[0],
        #                                     'lib',
        #                                     'phantom',
        #                                     'phantomjs.exe')
        #         driver = webdriver.PhantomJS(
        #                             executable_path=executable_path)
            # else:
            #     print('not implemented yet')
            #     sys.exit()
        # maximize driver window by default (fix)
        driver.maximize_window()

    return driver


def reset_driver_object():
    global driver 
    driver = None


def set_settings(settings_):
    global settings
    settings = settings_


def get_setting(setting):
    if setting in settings:
        return settings[setting]
    else:
        return False


def get_selected_driver():
    global driver_name
    if driver_name:
        driver_selected = driver_name
    else:
        driver_selected = 'firefox'
    return driver_selected
