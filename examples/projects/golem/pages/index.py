from golem.core import actions
from golem.selenium.utils import elements


create_project_button = ('css', "#projectCreationButton button", 'Create Project button')

title = ('css', "h4", 'Title')

project_name_input = ('id', "newProjectName", 'Project Name input')

create_button = ('id', "createProjectCreate", 'Create button')

project_list_item = ('css', '#projectList>a')

error_list_items = ('css', '#errorList li', 'error_list_item')

error_modal = ('id', 'errorModal', 'error_modal')


def verify_project_exists(project_name):
    actions.capture('verify the project exists in the list')
    items = elements(project_list_item)
    project_names = [x.text for x in items]
    if project_name not in project_names:
        raise Exception('Project {} does not exists'.format(project_name))


def verify_error_message(error_message):
    actions.wait_for_element_visible(error_modal)
    items = elements(error_list_items)
    error_messages = [x.text for x in items]
    actions.capture('verify the application shows the error message: {}'.format(error_message))
    if not error_message in error_messages:
        raise Exception('Error message {} is not present'.format(error_message))


def access_project(project_name):
    actions.add_step('Access project {}'.format(project_name))
    items = elements(project_list_item)
    for item in items:
        if item.text == project_name:
            item.click()
            return
    raise Exception('Project {} not found'.format(project_name))
