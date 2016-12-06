import os
import re

from golem.core import utils
from golem.gui import data, page_object


def _get_steps(content):

    index = -1
    steps = []
    for i, line in enumerate(content):
        if 'def test(self, data):' in line:
            index = i + 1
            break
    if index >= 0:
        end_of_steps = False
        while not end_of_steps:
            current_line = content[index]
            if len(current_line.strip()) and current_line.strip() != 'pass':
                # this is a step
                method_name = current_line.split('(')[0].strip()
                parameters = current_line.split('(')[1].split(')')[0]
                parameter_list = [x for x in parameters.split(',')]
                formatted_parameters = []
                for parameter in parameter_list:
                    if '\'' in parameter:
                        formatted_parameters.append(parameter.split('\'')[1])
                    else:
                        formatted_parameters.append(parameter)
                step = {
                    'method_name': method_name.replace('_', ' '),
                    'parameters': formatted_parameters
                }
                steps.append(step)
            if 'def teardown' in content[index + 1]:
                end_of_steps = True
            index += 1
    return steps


def get_page_objectsdeprecado(content):

    page_objects = []
    index = -1
    for i, line in enumerate(content):
        if 'pages' in line:
            index = i + 1
            break
    while 'class' not in content[index]:
        page_object_line = content[index]
        if 'import' in page_object_line:
            page_object = page_object_line.split('import')[1].strip()
            before_import = page_object_line.split('import')[0]
            rel_path = before_import.split('pages')[1].strip()
            if rel_path:
                if rel_path[0] == '.':
                    rel_path = rel_path[1:]
                rel_path += '.'
            po_with_rel_path = rel_path + page_object
            page_objects.append(po_with_rel_path)
        index += 1
    return page_objects


def get_page_objects(content):
    page_objects = []
    index = -1
    for i, line in enumerate(content):
        if 'pages' in line:
            index = i
            break
    pages_string = ''
    while True:
        pages_string += content[index]
        index += 1
        if ']' in pages_string:
            break
    pages_string = pages_string.replace('\n', '').strip().replace(' ', '')
    pages_string = pages_string.split('[')[1].split(']')[0]
    for page in pages_string.split(','):
        page_objects.append(page.replace("'", '').replace('"', ''))
    return page_objects


def get_description(content):

    content_string = ''.join(content)
    description = ''
    description = re.search(".*description = \'\'\'(.*\n*.*)\'\'\'",
                            content_string).group(1)
    description = re.sub("\s\s+", " ", description)
    return description


# def get_execute_script_content(content):

#     execute_script_content = []

#     save_content = False
#     level = 0
#     for line in content:
#         if save_content and '{' in line:
#             level += 1
#         if save_content and '}' in line:
#             if level > 0:
#                 level -= 1
#             else:
#                 save_content = False
#         if save_content:
#             execute_script_content.append(line)
#         if 'executeScript' in line:
#             save_content = True
#     return execute_script_content


def parse_test_case(workspace, project, parents, test_case_name):

    parents_joined = os.sep.join(parents)

    path = os.path.join(workspace,
                        'projects',
                        project,
                        'test_cases',
                        parents_joined,
                        test_case_name + '.py')

    with open(path) as f:
        content = f.readlines()

    description = get_description(content)
    page_objects = get_page_objects(content)
    steps = _get_steps(content)

    test_case = {
        'description': description,
        'page_objects': page_objects,
        'steps': steps,
    }
    return test_case


def new_test_case(root_path, project, parents, tc_name):
    parents_joined = os.sep.join(parents)

    test_case_path = os.path.join(
        root_path, 'projects', project, 'test_cases', parents_joined)
    if not os.path.exists(test_case_path):
        os.makedirs(test_case_path)
    test_case_full_path = os.path.join(test_case_path, tc_name + '.py')

    data_path = os.path.join(root_path,
                             'projects',
                             project,
                             'data',
                             parents_joined)
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    data_full_path = os.path.join(data_path, tc_name + '.csv')

    with open(test_case_full_path, 'w') as f:
        f.write(test_case_content.format(tc_name))

    with open(data_full_path, 'w') as f:
        f.write('')


test_case_content = """
class {0}:

    description = ''''''

    pages = []

    def setup(self):
        logger.description = self.description

    def test(self, data):
        pass

    def teardown(self):
        close()
"""


def format_parameters(step, root_path, project, parents, test_case_name):
    parameters = step['parameters']
    action = step['action'].replace(' ', '_')
    formatted_parameters = []
    for parameter in parameters:
        if page_object.is_page_object(parameter, root_path, project):
            # it is a page object, leave as is
            this_parameter_string = parameter
        else:
            # is not a page object,
            # identify if its a value or element parameter
            is_data_var = data.is_data_variable(root_path,
                                                project,
                                                parents,
                                                test_case_name,
                                                parameter)
            if is_data_var:
                this_parameter_string = 'data[\'{}\']'.format(parameter)
            else:
                if action in ['wait', 'select_by_index']:
                    this_parameter_string = parameter
                else:
                    this_parameter_string = '\'' + parameter + '\''
        formatted_parameters.append(this_parameter_string)

    all_parameters_string = ', '.join(formatted_parameters)
    return all_parameters_string


def format_page_object_string(page_objects):
    po_string = ''
    for po in page_objects:
        po_string = po_string + " '" + po + "',\n" + " " * 12
    po_string = "[{}]".format(po_string.strip()[:-1])
    return po_string


def save_test_case(root_path, project, full_test_case_name, description,
                   page_objects, test_steps):
    tc_name, parents = utils.separate_file_from_parents(full_test_case_name)
    test_case_path = os.path.join(root_path,
                                  'projects',
                                  project,
                                  'test_cases',
                                  os.sep.join(parents),
                                  '{}.py'.format(tc_name))

    with open(test_case_path, 'w') as f:
        f.write('\n')
        f.write('class {}:\n'.format(tc_name))
        f.write('\n')
        f.write('    description = \'\'\'{}\'\'\'\n'.format(description))
        f.write('\n')
        f.write('    pages = {}\n'
                .format(format_page_object_string(page_objects)))
        f.write('\n')
        f.write('    def setup(self):\n')
        f.write('        logger.description = self.description\n')
        f.write('\n')
        f.write('    def test(self, data):\n')
        if test_steps:
            for step in test_steps:
                parameters_formatted = format_parameters(step,
                                                         root_path,
                                                         project,
                                                         parents,
                                                         tc_name)
                f.write('        {0}({1})\n'
                        .format(step['action'].replace(' ', '_'),
                                parameters_formatted)
                        )
        else:
            f.write('        pass\n')
        f.write('\n')
        f.write('    def teardown(self):\n')
        f.write('        close()\n')
