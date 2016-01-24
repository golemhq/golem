from golem.core.exceptions import IncorrectSelectorType, ElementNotFound

from golem.gui import data

def get_selenium_object(obj, driver):
	if obj[0] == 'id':
		try:
			test_object = driver.find_element_by_id(obj[1])
		except:
			raise ElementNotFound('Element {0} not found using selector {1}:\'{2}\''
				.format(obj[2], obj[0], obj[1]))
	else:
		raise IncorrectSelectorType('Selector {0} is not a valid option'
			.format(obj[0]))
	
	return test_object


def get_test_data(root_path, project, parents, test_case_name):
	test_data = data.parse_test_data(root_path, project, parents, test_case_name)
	return test_data