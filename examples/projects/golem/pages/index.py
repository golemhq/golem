from golem.core import actions, getOrCreateWebdriver
from golem.core import selenium_utils, actions


create_project_button = ('css', "#projectCreationButton button", 'Create Project button')

title = ('css', "h4", 'Title')

project_name_input = ('id', "newProjectName", 'Project Name input')

create_button = ('id', "createProjectCreate", 'Create button')

project_list_item = ('css', '#projectList>a')

error_list_items = ('css', '#errorList li', 'error_list_item')

error_modal = ('id', 'errorModal', 'error_modal')


def verify_project_exists(project_name):
    driver = getOrCreateWebdriver()
    items = selenium_utils.get_selenium_objects(project_list_item, driver)
    project_names = [x.text for x in items]
    if project_name not in project_names:
        raise Exception('Project does not exists')


def verify_error_message(error_message):
    driver = getOrCreateWebdriver()
    actions.wait_for_element_visible(error_modal)
    items = selenium_utils.get_selenium_objects(error_list_items, driver)
    error_messages = [x.text for x in items]
    actions.capture('verify the application shows the error message: {}'.format(error_message))
    if not error_message in error_messages:
        raise Exception('Error message {} is not present'.format(error_message))


def access_project(project_name):
    actions.add_step('Access project {}'.format(project_name))
    driver = getOrCreateWebdriver()
    items = selenium_utils.get_selenium_objects(project_list_item, driver)
    for item in items:
        if item.text == project_name:
            item.click()
            return
    raise Exception('Project {} not found'.format(project_name))
