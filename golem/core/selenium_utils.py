import time

from selenium import webdriver

from golem import core
from golem.gui import data
from golem.core.exceptions import IncorrectSelectorType, ElementNotFound


def _find_selenium_object(selector_type, selector_value, element_name, driver, remaining_time):
    test_object = None
    start_time = time.time()
    try:
        if selector_type == 'id':
            test_object = driver.find_element_by_id(selector_value)
        elif selector_type == 'css':
            test_object = driver.find_element_by_css_selector(selector_value)
        elif selector_type == 'text':
            test_object = driver.find_element_by_css_selector("text[{}]".format(selector_value))
        elif selector_type == 'link_text':
            test_object = driver.find_element_by_link_text(selector_value)
        elif selector_type == 'partial_link_text':
            test_object = driver.find_element_by_partial_link_text(selector_value)
        elif selector_type == 'name':
            test_object = driver.find_element_by_name(selector_value)
        elif selector_type == 'xpath':
            test_object = driver.find_element_by_xpath(selector_value)
        elif selector_type == 'tag_name':
            test_object = driver.find_element_by_tag_name(selector_value)
        else:
            raise IncorrectSelectorType('Selector {0} is not a valid option'
                                .format(selector_type))
    except:
        time.sleep(0.5)
        end_time = time.time()
        new_remaining_time = remaining_time - (end_time - start_time)
        if new_remaining_time > 0:
            test_object = _find_selenium_object(selector_type, selector_value, element_name, 
                                                driver, new_remaining_time)
        else:
            raise ElementNotFound(
                    'Element {0} not found using selector {1}:\'{2}\''
                    .format(element_name, selector_type, selector_value))
    return test_object


def get_selenium_object(elem, driver):
    test_object = None
    implicit_wait = core.get_setting('implicit_wait')
    selector_type = elem[0]
    selector_value = elem[1]
    element_name = ''
    if len(elem) == 3:
        element_name = elem[2]
    test_object = _find_selenium_object(selector_type, selector_value, element_name, 
                                        driver, implicit_wait)
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
            print('not implemented yet')
            sys.exit()

    return driver
