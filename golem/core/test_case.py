"""Methods for dealing with test case modules
Test Cases are modules located inside the /tests/ directory
"""
import os
import re
import inspect

from golem.core import (utils,
                        test_execution,
                        file_manager,
                        settings_manager)
from golem.core import test_data as test_data_module

def _parse_step(step):
    """Parse a step string of a test function (setup, test or teardown)."""
    method_name = step.split('(', 1)[0].strip()
    # if not '.' in method_name:
    #     method_name = method_name.replace('_', ' ')
    # clean_param_list = []
    param_list = []

    params_re = re.compile('\((?P<args>.+)\)')
    params_search = params_re.search(step)
    if params_search:
        params_string = params_search.group('args')
        param_pairs = []
        inside_param = False
        inside_string = False
        string_char = ''
        current_start = 0
        for i in range(len(params_string)):
            is_last_char = i == len(params_string) -1
            is_higher_level_comma = False

            if params_string[i] == '\'':
                if not inside_string:
                    inside_string = True
                    string_char = '\''
                elif string_char == '\'':
                    inside_string = False

            if params_string[i] == '\"':
                if not inside_string:
                    inside_string = True
                    string_char = '\"'
                elif string_char == '\"':
                    inside_string = False

            if params_string[i] == ',' and not inside_param and not inside_string:
                is_higher_level_comma = True

            if params_string[i] in ['(', '{', '[']:
                inside_param = True
            elif inside_param and params_string[i] in [')', '}', ']']:
                inside_param = False

            if is_higher_level_comma:
                param_pairs.append((current_start, i))
                current_start = i + 1
            elif is_last_char:
                param_pairs.append((current_start, i+1))
                current_start = i + 2

        for pair in param_pairs:
            param_list.append(params_string[pair[0]:pair[1]])

        param_list = [x.strip() for x in param_list]
        # for param in param_list:
        #     # if 'data[' in param:
        #     #     data_re = re.compile("[\'|\"](?P<data>.*)[\'|\"]")
        #     #     g = data_re.search(param)
        #     #     clean_param_list.append(g.group('data'))
        #     if '(' in param and ')' in param:
        #         clean_param_list.append(param)
        #     else:
        #         # clean_param_list.append(param.replace('\'', '').replace('"', ''))
        #         clean_param_list.append(param)
    step = {
        'method_name': method_name,
        'parameters': param_list
    }
    return step


def _get_parsed_steps(function_code):
    """Get a list of parsed steps provided the code of a
    test function (setup, test or teardown)
    """
    steps = []
    code_lines = inspect.getsourcelines(function_code)[0]
    code_lines = [x.strip().replace('\n', '') for x in code_lines]
    code_lines.pop(0)
    for line in code_lines:
        if line != 'pass' and len(line):
            steps.append(_parse_step(line))
    return steps


def get_test_case_content(root_path, project, test_case_name):
    """Parse and return the contents of a Test in
    the following format:
      'description' :  string
      'pages' :        list of pages
      'steps' :        step dictionary
        'setup' :      parsed setup steps
        'test' :       parsed test steps
        'teardown' :   parsed teardown steps
    """
    test_contents = {
        'description': '',
        'pages': [],
        'steps': {
            'setup': [],
            'test': [],
            'teardown': []
        }
    }
    test_module = import_test_case_module(root_path, project, test_case_name)
    # get description
    description = getattr(test_module, 'description', '')
    
    # get list of pages
    pages = getattr(test_module, 'pages', [])
      
    # get setup steps
    setup_steps = []
    setup_function = getattr(test_module, 'setup', None)
    if setup_function:
        setup_steps = _get_parsed_steps(setup_function)
    
    # get test steps
    test_steps = []
    test_function = getattr(test_module, 'test', None)
    if test_function:
        test_steps = _get_parsed_steps(test_function)
    
    # get teardown steps
    teardown_steps = []
    teardown_function = getattr(test_module, 'teardown', None)
    if teardown_function:
        teardown_steps = _get_parsed_steps(teardown_function)

    test_contents['description'] = description
    test_contents['pages'] = pages
    test_contents['steps']['setup'] = setup_steps
    test_contents['steps']['test'] = test_steps
    test_contents['steps']['teardown'] = teardown_steps
    return test_contents


def get_test_case_code(path):
    """Get test case content as a string
    provided the full path to the python file.
    """
    code = ''
    with open(path) as ff:
        code = ff.read()
    return code


def new_test_case(root_path, project, parents, tc_name):
    test_base = settings_manager.get_project_settings(root_path, project)['base_name']
    """Create a new empty test case."""
    test_case_content = (
        "\n"
        "description = ''\n\n"
        "pages = []\n\n"
        "def setup(data):\n"
        "    {}.setup(data)\n\n"
        "def test(data):\n"
        "    pass\n\n"
        "def teardown(data):\n"
        "    {}.teardown(data)\n\n".format(test_base, test_base))

    errors = []
    # check if a file already exists
    base_path = os.path.join(root_path, 'projects', project, 'tests')
    full_path = os.path.join(base_path, os.sep.join(parents))
    filepath = os.path.join(full_path, '{}.py'.format(tc_name))

    if tc_name == test_base:
        errors.append('base testcase will be generated automatically')
    elif os.path.isfile(filepath):
        errors.append('a test with that name already exists')
    if not errors:
        # create the directory structure if it does not exist
        if not os.path.isdir(full_path):
            for parent in parents:
                base_path = os.path.join(base_path, parent)
                file_manager.create_directory(path=base_path, add_init=True)
        
        with open(filepath, 'w') as test_file:
            test_file.write(test_case_content)
        print('Test {} created for project {}'.format(tc_name, project))
        new_base_test_case(root_path, project, parents, test_base)
    return errors

def new_base_test_case(root_path, project, parents, test_base):

    """Create a Test Base page."""
    test_case_content = (
        "\n\n"
        "description = 'Gereral setup and teardown for all testcases'\n\n"
        "pages = []\n\n"
        "def setup(data):\n"
        "    pass\n\n"
        "def teardown(data):\n"
        "    pass\n\n")
    # check if a file already exists
    base_path = os.path.join(root_path, 'projects', project, 'tests')
    full_path = os.path.join(base_path, os.sep.join(parents))
    filepath = os.path.join(full_path, '{}.py'.format(test_base))
    if not os.path.isfile(filepath):
        # create the directory structure if it does not exist
        if not os.path.isdir(full_path):
            for parent in parents:
                base_path = os.path.join(base_path, parent)
                file_manager.create_directory(path=base_path, add_init=True)
        
        with open(filepath, 'w') as test_file:
            test_file.write(test_case_content)
        print('{} page created for project {}'.format(test_base, project))

def _format_page_object_string(page_objects):
    """Format page object string to store in test case."""
    po_string = ''
    for page in page_objects:
        po_string = po_string + " '" + page + "',\n" + " " * 8
    po_string = "[{}]".format(po_string.strip()[:-1])
    return po_string


def _format_description(description):
    """Format description string to store in test case."""
    formatted_description = ''
    description = description.replace('"', '\\"').replace("'", "\\'")
    if '\n' in description:
        desc_lines = description.split('\n')
        formatted_description = 'description = \'\'\''
        for line in desc_lines:
            formatted_description = formatted_description + '\n' + line
        formatted_description = formatted_description + '\'\'\'\n'
    else:
        formatted_description = 'description = \'{}\'\n'.format(description)
    return formatted_description


def _format_data(test_data):
    """Format data string to store in test case."""
    result = '[\n'
    for data_set in test_data:
        result += '    {\n'
        for key, value in data_set.items():
            if not value:
                value = "''"
            result += '        \'{}\': {},\n'.format(key, value)
        result += '    },\n'
    result += ']\n\n'
    return result


def generate_test_case_path(root_path, project, full_test_case_name):
    """Generate full path to a python file of a test case.
    
    full_test_case_name must be a dot path starting from /tests/ dir.
    Example:
      generate_test_case_path('/', 'project1', 'module1.test1')
      -> '/projects/project1/tests/module1/test1.py'
    """
    tc_name, parents = utils.separate_file_from_parents(full_test_case_name)
    test_case_path = os.path.join(root_path, 'projects', project, 'tests',
                                  os.sep.join(parents), '{}.py'.format(tc_name))
    return test_case_path


def save_test_case(root_path, project, full_test_case_name, description,
                   page_objects, test_steps, test_data):
    """Save test case contents to file.

    full_test_case_name is a relative dot path to the test
    """
    print("save_test_case "+full_test_case_name)
    test_case_path = generate_test_case_path(root_path, project,
                                             full_test_case_name)
    formatted_description = _format_description(description)
    with open(test_case_path, 'w', encoding='utf-8') as f:
        # write description
        f.write('\n')
        f.write(formatted_description)
        f.write('\n')
        # write the list of pages
        f.write('pages = {}\n'.format(_format_page_object_string(page_objects)))
        f.write('\n')
        # write test data if required or save test data to external file
        if test_execution.settings['test_data'] == 'infile':
            if test_data:
                f.write('data = {}'.format(_format_data(test_data)))
                test_data_module.remove_csv_if_exists(root_path, project, full_test_case_name)
        else:
            test_data_module.save_external_test_data_file(root_path, project,
                                                          full_test_case_name,
                                                          test_data)
        # write the setup function
        f.write('def setup(data):\n')
        if test_steps['setup']:
            for step in test_steps['setup']:
                step_action = step['action'].replace(' ', '_')
                param_str = ', '.join(step['parameters'])
                f.write('    {0}({1})\n'.format(step_action, param_str))
        else:
            f.write('    pass\n')
        f.write('\n')
        # write the test function
        f.write('def test(data):\n')
        if test_steps['test']:
            for step in test_steps['test']:
                step_action = step['action'].replace(' ', '_')
                param_str = ', '.join(step['parameters'])
                f.write('    {0}({1})\n'.format(step_action, param_str))
        else:
            f.write('    pass\n')
        f.write('\n')
        # write the teardown function
        f.write('def teardown(data):\n')
        if test_steps['teardown']:
            for step in test_steps['teardown']:
                step_action = step['action'].replace(' ', '_')
                param_str = ', '.join(step['parameters'])
                f.write('    {0}({1})\n'.format(step_action, param_str))
        else:
            f.write('    pass\n')


def save_test_case_code(root_path, project, full_test_case_name,
                        content, table_test_data):
    """Save test case contents string to file.
    full_test_case_name is a relative dot path to the test.
    """
    test_case_path = generate_test_case_path(root_path, project, full_test_case_name)
    with open(test_case_path, 'w') as test_file:
        test_file.write(content)
    # save test data
    if test_execution.settings['test_data'] == 'csv':
        #save csv data
        test_data_module.save_external_test_data_file(root_path, project,
                                                      full_test_case_name,
                                                      table_test_data)
    elif test_execution.settings['test_data'] == 'infile':
        # remove csv files
        test_data_module.remove_csv_if_exists(root_path, project, full_test_case_name)


def test_case_exists(workspace, project, full_test_case_name):
    """Test case exists.

    full_test_case_name is a relative dot path to the test.
    """
    test, parents = utils.separate_file_from_parents(full_test_case_name)
    path = os.path.join(workspace, 'projects', project, 'tests',
                        os.sep.join(parents), '{}.py'.format(test))
    return os.path.isfile(path)


def import_test_case_module(workspace, project, full_test_case_name):
    path = generate_test_case_path(workspace, project, full_test_case_name)
    module, _ = utils.import_module(path)
    return module