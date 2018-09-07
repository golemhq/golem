"""Methods for dealing with suite modules
Suites are modules located inside the /suites/ directory
"""
import os
import importlib

from golem.core import utils, file_manager, settings_manager


def _format_list_items(list_items):
    """Generate an indented string out of a list of items."""
    list_string = ''
    if list_items:
        for item in list_items:
            list_string = list_string + "    '" + item + "',\n"
        list_string = "[\n    {}\n]".format(list_string.strip()[:-1])
    else:
        list_string = '[]'
    return list_string


def save_suite(root_path, project, suite_name, test_cases, workers,
               browsers, environments):
    """Save suite content to file."""
    suite_name, parents = utils.separate_file_from_parents(suite_name)

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
    """Create a new empty suite."""
    suite_content = ('\n'
                     'browsers = []\n\n'
                     'environments = []\n\n'
                     'workers = 1\n\n'
                     'tests = []\n')
    errors = []
    base_path = os.path.join(root_path, 'projects', project, 'suites')
    full_path = os.path.join(base_path, os.sep.join(parents))
    filepath = os.path.join(full_path, '{}.py'.format(suite_name))
    if os.path.isfile(filepath):
        errors.append('a suite with that name already exists')
    if not errors:
        # create the directory structure if it does not exist
        if not os.path.isdir(full_path):
            for parent in parents:
                base_path = os.path.join(base_path, parent)
                file_manager.create_directory(path=base_path, add_init=True)
        with open(filepath, 'w') as suite_file:
            suite_file.write(suite_content)
        print('Suite {} created for project {}'.format(suite_name, project))
    return errors


def get_suite_amount_of_workers(workspace, project, suite):
    """Get the amount of workers defined in a suite.
    Default is 1 if suite does not have workers defined"""
    amount = 1
    suite_module = get_suite_module(workspace, project, suite)
    if hasattr(suite_module, 'workers'):
        amount = suite_module.workers
    return amount


def get_suite_environments(workspace, project, suite):
    """Get the environments defined in a suite."""
    environments = []
    suite_module = get_suite_module(workspace, project, suite)
    if hasattr(suite_module, 'environments'):
        environments = suite_module.environments

    return environments


def get_suite_test_cases(workspace, project, suite):
    """Return a list with all the test cases of a given suite"""
    # TODO should use glob
    tests = []
    suite_module = get_suite_module(workspace, project, suite)
    if '*' in suite_module.tests:
        path = os.path.join(workspace, 'projects', project, 'tests')
        tests = file_manager.get_files_dot_path(path, extension='.py')
    else:
        for test in suite_module.tests:
            if test[-1] == '*':
                this_dir = os.path.join(test[:-2])
                path = os.path.join(workspace, 'projects', project,
                                    'tests', this_dir)
                this_dir_tests = file_manager.get_files_dot_path(path, extension='.py')
                this_dir_tests = ['{}.{}'.format(this_dir, x) for x in this_dir_tests]
                tests = tests + this_dir_tests
            else:
                tests.append(test)
    base_name = settings_manager.get_project_settings(workspace, project)['base_name']
    for test in tests:
        if test.split(".")[-1] == base_name:
            tests.remove(test)
    return tests


def get_suite_browsers(workspace, project, suite):
    """Get the list of browsers defined in a suite"""
    browsers = []
    suite_module = get_suite_module(workspace, project, suite)
    if hasattr(suite_module, 'browsers'):
        browsers = suite_module.browsers

    return browsers


def get_suite_module(workspace, project, suite_name):
    """Get the module of a suite"""
    suite_name, parents = utils.separate_file_from_parents(suite_name)
    path = os.path.join(workspace, 'projects', project, 'suites',
                        os.sep.join(parents), suite_name + '.py')
    suite_module, _ = utils.import_module(path)
    return suite_module


def suite_exists(workspace, project, full_suite_name):
    """suite exists.
    full_suite_name must be a relative dot path
    """
    suite, parents = utils.separate_file_from_parents(full_suite_name)
    path = os.path.join(workspace, 'projects', project, 'suites',
                        os.sep.join(parents), '{}.py'.format(suite))
    return os.path.isfile(path)