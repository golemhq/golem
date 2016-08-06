from selenium import webdriver

from golem.gui import data
from golem.core.exceptions import IncorrectSelectorType, ElementNotFound


def get_selenium_object(obj, driver):
	if obj[0] == 'id':
		try:
			test_object = driver.find_element_by_id(obj[1])
		except:
			raise ElementNotFound('Element {0} not found using selector {1}:\'{2}\''
				.format(obj[2], obj[0], obj[1]))
	elif obj[0] == 'css':
		try:
			test_object = driver.find_element_by_css_selector(obj[1])
		except:
			raise ElementNotFound('Element {0} not found using selector {1}:\'{2}\''
				.format(obj[2], obj[0], obj[1]))
	elif obj[0] == 'text':
		try:
			test_object = driver.find_element_by_css_selector("text[{}]".format(obj[1]))
		except:
			raise ElementNotFound('Element {0} not found using selector {1}:\'{2}\''
				.format(obj[2], obj[0], obj[1]))
	elif obj[0] == 'name':
		try:
			test_object = driver.find_element_by_name(obj[1])
		except:
			raise ElementNotFound('Element {0} not found using selector {1}:\'{2}\''
				.format(obj[2], obj[0], obj[1]))
	else:
		raise IncorrectSelectorType('Selector {0} is not a valid option'
			.format(obj[0]))
	
	return test_object


def get_test_or_suite_data(root_path, project, parents, test_case_name):
	test_data = data.parse_test_data(root_path, project, parents, test_case_name)
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
            a = os.path.dirname(os.path.abspath(__file__))
            b = os.path.abspath(os.path.join( a , os.pardir))
            driver = webdriver.PhantomJS(executable_path= b + '\\lib\\phantom\\phantomjs.exe')
        else:
            print 'not implemented yet'
            sys.exit()

    return driver