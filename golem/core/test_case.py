import os
import re
import importlib
import inspect

from golem.core import utils, data, page_object


def _parse_step(step):
    # ('a')                 -> ['a']
    # ('a', 'b')            -> ['a', 'b']
    # ('a, b, c')           -> ['a, b, c']
    # (('a', 'b', 'c'))     -> ['(\'a\', \'b\', \'c\')']
    print(step)
    method_name = step.split('(', 1)[0].strip()
    if not '.' in method_name:
        method_name = method_name.replace('_', ' ')
    clean_param_list = []

    params_re = re.compile('\((?P<args>.+)\)')
    params_search = params_re.search(step)
    if params_search:
        params_string = params_search.group('args')
        param_list = []
        param_pairs = []
        inside_param = False
        inside_string = False
        string_char = ''
        current_start = 0
        print('PARAM STRING', params_string)
        for i in range(len(params_string)):
            is_last_char = i == len(params_string) -1
            is_higher_level_comma = False
            
            if params_string[i] == '\'':
                if not inside_string:
                    inside_string = True
                    string_char = '\''
                elif string_char == '\'':
                    inside_string = False

            if params_string[i] == ',' and not inside_param and not inside_string:
                is_higher_level_comma = True

            if params_string[i] == '(' or params_string[i] == '{':
                inside_param = True
            elif inside_param and (params_string[i] == ')' or params_string[i] == '}'):
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
        print(param_list)
        for param in param_list:

            # if 'data[' in param:
            #     data_re = re.compile("[\'|\"](?P<data>.*)[\'|\"]")
            #     g = data_re.search(param)
            #     clean_param_list.append(g.group('data'))
            print('PARAM', param)
            if '(' in param and ')' in param:
                clean_param_list.append(param)
            else:
                clean_param_list.append(param.replace('\'', '').replace('"', ''))
    step = {
        'method_name': method_name,
        'parameters': clean_param_list
    }
    return step


def _get_parsed_steps(function_code):
    steps = []
    code_lines = inspect.getsourcelines(function_code)[0]
    code_lines = [x.strip().replace('\n', '') for x in code_lines]
    code_lines.pop(0)
    for line in code_lines:
        if line != 'pass':
            steps.append(_parse_step(line))
    return steps


def get_test_case_content(project, test_case_name):
    test_contents = {}
    test_module = importlib.import_module('projects.{0}.tests.{1}'
                                          .format(project, test_case_name))
    # get description
    description = getattr(test_module, 'description', '')
    # get list of pages
    pages = getattr(test_module, 'pages', [])
    # get setup steps
    setup_steps = []
    setup_function_code = getattr(test_module, 'setup', None)
    if setup_function_code:
        setup_steps = _get_parsed_steps(setup_function_code)
    # get test steps
    test_steps = []
    test_function_code = getattr(test_module, 'test', None)
    if test_function_code:
        test_steps = _get_parsed_steps(test_function_code)
    # get teardown steps
    teardown_steps = []
    teardown_function_code = getattr(test_module, 'teardown', None)
    if teardown_function_code:
        teardown_steps = _get_parsed_steps(teardown_function_code)
    
    test_contents['description'] = description
    test_contents['pages'] = pages
    test_contents['steps'] = {
        'setup': setup_steps,
        'test' : test_steps,
        'teardown': teardown_steps
    }
    content = ''
    try:
        content = inspect.getsource(test_module)
    except:
        pass
    test_contents['content'] = content
    return test_contents


def new_test_case(root_path, project, parents, tc_name):
    test_case_content = (
        "\n"
        "description = ''\n\n"
        "pages = []\n\n"
        "def setup(data):\n"
        "    pass\n\n"
        "def test(data):\n"
        "    pass\n\n"
        "def teardown(data):\n"
        "    pass\n\n")
    errors = []
    # check if a file already exists
    path = os.path.join(root_path, 'projects', project, 'tests',
                        os.sep.join(parents), '{}.py'.format(tc_name))
    if os.path.isfile(path):
        errors.append('A test with that name already exists')
    if not errors:
        parents_joined = os.sep.join(parents)
        base_path = os.path.join(root_path, 'projects', project, 'tests')
        test_case_path = os.path.join(base_path, parents_joined)
        # create the directory structure if it does not exist
        if not os.path.exists(test_case_path):
            for parent in parents:
                base_path = os.path.join(base_path, parent)
                utils.create_new_directory(path=base_path, add_init=True)
        test_case_full_path = os.path.join(test_case_path, tc_name + '.py')
        data_path = os.path.join(root_path, 'projects', project, 'data', parents_joined)
        if not os.path.exists(data_path):
            os.makedirs(data_path)
        data_full_path = os.path.join(data_path, tc_name + '.csv')
        with open(test_case_full_path, 'w') as f:
            f.write(test_case_content)
        with open(data_full_path, 'w') as f:
            f.write('')
    return errors


def format_parameters(step, root_path, project, parents, test_case_name, stored_keys):
    parameters = step['parameters']
    action = step['action'].replace(' ', '_')
    formatted_parameters = []
    for parameter in parameters:
        if parameter:
            this_parameter_string = ''
            if page_object.is_page_object(parameter, root_path, project):
                # it is a page object, leave as is
                this_parameter_string = parameter
            elif 'random(' in parameter:
                this_parameter_string = parameter
            else:
                # is not a page object,
                # identify if its a value or element parameter
                
                # is_data_var = data.is_data_variable(root_path, project, parents,
                #                                     test_case_name, parameter)

                is_data_var = 'data.' in parameter

                is_in_stored_keys = parameter in stored_keys
                action_is_store = action == 'store'
                if (is_data_var or is_in_stored_keys) and not action_is_store:
                    # this_parameter_string = 'data[\'{}\']'.format(parameter)
                    this_parameter_string = parameter
                else:
                    if action in ['wait', 'select_by_index']:
                        this_parameter_string = parameter
                    elif parameter[0] == '(' and parameter[-1] == ')':
                        this_parameter_string = parameter
                    else:
                        this_parameter_string = '\'' + parameter + '\''
            formatted_parameters.append(this_parameter_string)

    all_parameters_string = ', '.join(formatted_parameters)
    return all_parameters_string


def format_page_object_string(page_objects):
    po_string = ''
    for po in page_objects:
        po_string = po_string + " '" + po + "',\n" + " " * 8
    po_string = "[{}]".format(po_string.strip()[:-1])
    return po_string


def format_description(description):
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


def get_stored_keys(steps):
    stored_keys = []
    for step in steps:
        parameters = step['parameters']
        action = step['action'].replace(' ', '_')
        if action == 'store':
            stored_keys.append(parameters[0])
    return stored_keys


def save_test_case(root_path, project, full_test_case_name, description,
                   page_objects, test_steps):
    tc_name, parents = utils.separate_file_from_parents(full_test_case_name)
    test_case_path = os.path.join(root_path, 'projects', project, 'tests',
                                  os.sep.join(parents), '{}.py'.format(tc_name))
    setup_stored_keys = get_stored_keys(test_steps['setup']) 
    test_stored_keys = get_stored_keys(test_steps['test'])
    teardown_stored_keys = get_stored_keys(test_steps['teardown'])

    
    formatted_description = format_description(description)

    with open(test_case_path, 'w', encoding='utf-8') as f:
        # write description
        f.write('\n')
        f.write(formatted_description)
        f.write('\n')
        # write the list of pages
        f.write('pages = {}\n'.format(format_page_object_string(page_objects)))
        f.write('\n')
        # write the setup function
        f.write('def setup(data):\n')
        if test_steps['setup']:
            for step in test_steps['setup']:
                parameters_formatted = format_parameters(step, root_path, project,
                                                         parents, tc_name,
                                                         setup_stored_keys)
                f.write('    {0}({1})\n'
                        .format(step['action'].replace(' ', '_'),
                                parameters_formatted))
        else:
            f.write('    pass\n')
        f.write('\n')
        # write the test function
        f.write('def test(data):\n')
        if test_steps['test']:
            for step in test_steps['test']:
                parameters_formatted = format_parameters(step, root_path, project,
                                                         parents, tc_name,
                                                         test_stored_keys)
                f.write('    {0}({1})\n'
                        .format(step['action'].replace(' ', '_'),
                                parameters_formatted))
        else:
            f.write('    pass\n')
        f.write('\n\n')
        # write the teardown function
        f.write('def teardown(data):\n')
        if test_steps['teardown']:
            for step in test_steps['teardown']:
                parameters_formatted = format_parameters(step, root_path, project,
                                                         parents, tc_name,
                                                         teardown_stored_keys)
                f.write('    {0}({1})\n'
                        .format(step['action'].replace(' ', '_'),
                                parameters_formatted))
        else:
            f.write('    pass\n')


def save_test_case_code(root_path, project, full_test_case_name, content):
    tc_name, parents = utils.separate_file_from_parents(full_test_case_name)
    test_case_path = os.path.join(root_path, 'projects', project, 'tests',
                                  os.sep.join(parents), '{}.py'.format(tc_name))
    with open(test_case_path, 'w', encoding='utf-8') as f:
        f.write(content)
