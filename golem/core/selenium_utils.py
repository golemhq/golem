import time

from selenium import webdriver

from golem import core
from golem.gui import data
from golem.core.exceptions import IncorrectSelectorType, ElementNotFound


def _find_selenium_object(obj, driver, remaining_time):
    test_object = None
    start_time = time.time()
    try:
        if obj[0] == 'id':
            test_object = driver.find_element_by_id(obj[1])
        elif obj[0] == 'css':
            test_object = driver.find_element_by_css_selector(obj[1])
        elif obj[0] == 'text':
            test_object = driver.find_element_by_css_selector(
                                        "text[{}]".format(obj[1]))
        elif obj[0] == 'link_text':
            test_object = driver.find_element_by_link_text(obj[1])
        elif obj[0] == 'partial_link_text':
            test_object = driver.find_element_by_partial_link_text(obj[1])
        elif obj[0] == 'name':
            test_object = driver.find_element_by_name(obj[1])
        elif obj[0] == 'xpath':
            test_object = driver.find_element_by_xpath(obj[1])
        elif obj[0] == 'tag_name':
            test_object = driver.find_element_by_tag_name(obj[1])
        else:
            raise IncorrectSelectorType('Selector {0} is not a valid option'
                                .format(obj[0]))
    except:
        time.sleep(0.5)
        end_time = time.time()
        new_remaining_time = remaining_time - (end_time - start_time)
        if new_remaining_time > 0:
            test_object = _find_selenium_object(obj, driver, new_remaining_time)
        else:
            raise ElementNotFound(
                    'Element {0} not found using selector {1}:\'{2}\''
                    .format(obj[2], obj[0], obj[1]))
    return test_object


def get_selenium_object(obj, driver):
    test_object = None
    implicit_wait = core.get_setting('implicit_wait')
    test_object = _find_selenium_object(obj, driver, implicit_wait)
    return test_object


def get_test_or_suite_data(root_path, project, parents, test_case_name):
    test_data = data.parse_test_data(
                        root_path,
                        project,
                        parents,
                        test_case_name)
    return test_data


def get_driver(driver_selected):
    driver = None

    if driver_selected == 'firefox':
        driver = webdriver.Firefox()
    if driver_selected == 'chrome':
        driver = webdriver.Chrome()
    if driver_selected == 'ie':
        driver = webdriver.Ie()
    if driver_selected == 'phantomjs':
        if os.name == 'nt':
            executable_path = os.path.join(
                                        golem.__path__[0],
                                        'lib',
                                        'phantom',
                                        'phantomjs.exe')
            driver = webdriver.PhantomJS(
                                executable_path=executable_path)
        else:
            print 'not implemented yet'
            sys.exit()

    return driver
