from golem.core import actions, getOrCreateWebdriver
from golem.core import selenium_utils


create_project_button = ('css', "#projectCreationButton button", 'Create Project button')

title = ('css', "h4", 'Title')

project_name_input = ('id', "newProjectName", 'Project Name input')

create_button = ('id', "createProjectCreate", 'Create button')

project_list_item = ('css', '#projectList>a')


def verify_project_exists(project_name):
    driver = getOrCreateWebdriver()
    items = selenium_utils.get_selenium_objects(project_list_item, driver)
    project_names = [x.text for x in items]
    if project_name not in project_names:
        raise Exception('Project does not exists')
