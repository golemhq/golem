import os


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
    suite_path = os.path.join(root_path, 'projects', project, 'suites',
                              '{}.py'.format(suite))
    with open(suite_path, 'w', encoding='utf-8') as suite_file:
        suite_file.write('\n\n')
        suite_file.write('browsers = {}\n'.format(_format_list_items(browsers)))
        suite_file.write('\n')
        suite_file.write('environments = {}\n'.format(_format_list_items(environments)))
        suite_file.write('\n')
        suite_file.write('workers = {}'.format(workers))
        suite_file.write('\n\n')
        suite_file.write('tests = {}\n'.format(_format_list_items(test_cases)))


def new_suite(root_path, project, suite_name):
    errors = []
    path = os.path.join(root_path, 'projects', project, 'suites', '{}.py'.format(suite_name))
    if os.path.isfile(path):
        errors.append('A suite with that name already exists')

    if not errors:
        suite_path = os.path.join(root_path, 'projects', project, 'suites')
        suite_full_path = os.path.join(suite_path, suite_name + '.py')
        test_case_content = ('\n'
                             'browsers = []\n\n'
                             'environments = []\n\n'
                             'workers = 1\n\n'
                             'tests = []\n')
        with open(suite_full_path, 'w') as suite_file:
            suite_file.write(test_case_content)
    return errors
