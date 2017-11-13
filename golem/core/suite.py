import os

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
