import os
import importlib

from golem.core import utils


def _format_list_items(list_items):
    list_string = ''
    if list_items:
        for item in list_items:
            list_string = list_string + "    '" + item + "',\n"
        list_string = "[\n    {}\n]".format(list_string.strip()[:-1])
    else:
        list_string = '[]'
    return list_string


def save_suite(root_path, project, suite, test_cases, workers, browsers, environments):
    suite_name, parents = utils.separate_file_from_parents(suite)

    suite_path = os.path.join(root_path, 'projects', project, 'suites',
                              os.sep.join(parents), '{}.py'.format(suite_name))
    with open(suite_path, 'w', encoding='utf-8') as suite_file:
        suite_file.write('\n\n')
        suite_file.write('browsers = {}\n'.format(_format_list_items(browsers)))
        suite_file.write('\n')
        suite_file.write('environments = {}\n'.format(_format_list_items(environments)))
        suite_file.write('\n')
        suite_file.write('workers = {}'.format(workers))
        suite_file.write('\n\n')
        suite_file.write('tests = {}\n'.format(_format_list_items(test_cases)))


def new_suite(root_path, project, parents, suite_name):
    errors = []
    path = os.path.join(root_path, 'projects', project, 'suites',
                        os.sep.join(parents), '{}.py'.format(suite_name))
    if os.path.isfile(path):
        errors.append('A suite with that name already exists')
    if not errors:
        suite_content = ('\n'
                         'browsers = []\n\n'
                         'environments = []\n\n'
                         'workers = 1\n\n'
                         'tests = []\n')
        with open(path, 'w') as suite_file:
            suite_file.write(suite_content)
        print('Suite {} created for project {}'.format(suite_name, project))
    return errors


def get_suite_amount_of_workers(workspace, project, suite):
    amount = 1
    suite_module = importlib.import_module('projects.{0}.suites.{1}'.format(project, suite),
                                           package=None)
    if hasattr(suite_module, 'workers'):
        amount = suite_module.workers

    return amount


def get_suite_environments(workspace, project, suite):
    environments = []
    module_name = 'projects.{0}.suites.{1}'.format(project, suite)
    suite_module = importlib.import_module(module_name, package=None)
    if hasattr(suite_module, 'environments'):
        environments = suite_module.environments

    return environments


def get_suite_test_cases(workspace, project, suite):
    '''Return a list with all the test cases of a given suite'''
    tests = []
    module_name = 'projects.{0}.suites.{1}'.format(project, suite)
    suite_module = importlib.import_module(module_name, package=None)
    if '*' in suite_module.tests:
        path = os.path.join(workspace, 'projects', project, 'tests')
        tests = utils.get_files_in_directory_dot_path(path)
    else:
        for test in suite_module.tests:
            if test[-1] == '*':
                this_dir = os.path.join(test[:-2])
                path = os.path.join(workspace, 'projects', project,
                                    'tests', this_dir)
                this_dir_tests = utils.get_files_in_directory_dot_path(path)
                this_dir_tests = ['{}.{}'.format(this_dir, x) for x in this_dir_tests]
                tests = tests + this_dir_tests
            else:
                tests.append(test)
    return tests


def get_suite_browsers(workspace, project, suite):
    browsers = []
    module_name = 'projects.{0}.suites.{1}'.format(project, suite)
    suite_module = importlib.import_module(module_name, package=None)
    if hasattr(suite_module, 'browsers'):
        browsers = suite_module.browsers

    return browsers


def get_suite_module(workspace, project, suite):
    module_name = 'projects.{0}.suites.{1}'.format(project, suite)
    suite_module = importlib.import_module(module_name, package=None)
    return suite_module
