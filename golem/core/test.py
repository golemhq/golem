import os
import re
import inspect
import shutil

from golem.core import file_manager, settings_manager
from golem.core import test_data as test_data_module
from golem.core.project import Project, validate_project_element_name, BaseProjectElement


def create_test(project_name, test_name):
    test_content = (
        "\n"
        "description = ''\n\n"
        "tags = []\n\n"
        "pages = []\n\n"
        "def setup(data):\n"
        "    pass\n\n"
        "def test(data):\n"
        "    pass\n\n"
        "def teardown(data):\n"
        "    pass\n\n")
    errors = []
    project = Project(project_name)
    test_name = test_name.strip().replace(' ', '_')
    if test_name in project.tests():
        errors.append('A test with that name already exists')
    else:
        errors = validate_project_element_name(test_name)
    if not errors:
        project.create_packages_for_element(test_name, 'test')
        path = Test(project_name, test_name).path
        with open(path, 'w') as f:
            f.write(test_content)
        print('Test {} created for project {}'.format(test_name, project_name))
    return errors


def rename_test(project_name, test_name, new_test_name):
    errors = []
    project = Project(project_name)
    new_test_name = new_test_name.strip().replace(' ', '_')
    if test_name not in project.tests():
        errors.append('Test {} does not exist'.format(test_name))
    else:
        errors = validate_project_element_name(new_test_name)
    if not errors:
        old_path = Test(project_name, test_name).path
        new_path = Test(project_name, new_test_name).path
        project.create_packages_for_element(new_test_name, 'test')
        errors = file_manager.rename_file(old_path, new_path)
        # try to rename data file in /tests/ folder
        old_data_path = os.path.splitext(old_path)[0] + '.csv'
        new_data_path = os.path.splitext(new_path)[0] + '.csv'
        if os.path.isfile(old_data_path):
            errors = file_manager.rename_file(old_data_path, new_data_path)
    return errors


def duplicate_test(project, name, new_name):
    errors = []
    old_path = Test(project, name).path
    new_path = Test(project, new_name).path
    new_name = new_name.strip().replace(' ', '_')
    if name == new_name:
        errors.append('New test name cannot be the same as the original')
    elif not os.path.isfile(old_path):
        errors.append('Test {} does not exist'.format(name))
    elif os.path.isfile(new_path):
        errors.append('A test with that name already exists')
    else:
        errors = validate_project_element_name(new_name)
    if not errors:
        try:
            Project(project).create_packages_for_element(new_name, 'test')
            file_manager.create_directory(path=os.path.dirname(new_path), add_init=True)
            shutil.copyfile(old_path, new_path)
            # duplicate data file if present
            old_data_path = os.path.splitext(old_path)[0] + '.csv'
            new_data_path = os.path.splitext(new_path)[0] + '.csv'
            if os.path.isfile(old_data_path):
                shutil.copyfile(old_data_path, new_data_path)
        except:
            errors.append('There was an error creating the new test')
    return errors


def edit_test(project, test_name, description, pages, test_steps, test_data, tags):
    """Save test contents to file"""
    path = Test(project, test_name).path
    formatted_description = _format_description(description)
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n')
        f.write(formatted_description)
        f.write('\n')
        f.write('tags = {}\n'.format(_format_tags_string(tags)))
        f.write('\n')
        f.write('pages = {}\n'.format(_format_page_object_string(pages)))
        f.write('\n')
        settings = settings_manager.get_project_settings(project)
        if settings['test_data'] == 'infile':
            if test_data:
                f.write('data = {}'.format(_format_data(test_data)))
                test_data_module.remove_csv_if_exists(project, test_name)
        else:
            test_data_module.save_external_test_data_file(project, test_name, test_data)
        f.write('def setup(data):\n')
        if test_steps['setup']:
            for step in test_steps['setup']:
                step_action = step['action'].replace(' ', '_')
                param_str = ', '.join(step['parameters'])
                f.write('    {0}({1})\n'.format(step_action, param_str))
        else:
            f.write('    pass\n')
        f.write('\n')
        f.write('def test(data):\n')
        if test_steps['test']:
            for step in test_steps['test']:
                step_action = step['action'].replace(' ', '_')
                param_str = ', '.join(step['parameters'])
                f.write('    {0}({1})\n'.format(step_action, param_str))
        else:
            f.write('    pass\n')
        f.write('\n')
        f.write('def teardown(data):\n')
        if test_steps['teardown']:
            for step in test_steps['teardown']:
                step_action = step['action'].replace(' ', '_')
                param_str = ', '.join(step['parameters'])
                f.write('    {0}({1})\n'.format(step_action, param_str))
        else:
            f.write('    pass\n')


def edit_test_code(project, test_name, content, table_test_data):
    path = Test(project, test_name).path
    with open(path, 'w') as f:
        f.write(content)
    # save test data
    settings = settings_manager.get_project_settings(project)
    if settings['test_data'] == 'csv':
        # save csv data
        test_data_module.save_external_test_data_file(project, test_name, table_test_data)
    elif settings['test_data'] == 'infile':
        # remove csv files
        test_data_module.remove_csv_if_exists(project, test_name)


def delete_test(project, test_name):
    errors = []
    path = Test(project, test_name).path
    if not os.path.isfile(path):
        errors.append('Test {} does not exist'.format(test_name))
    else:
        try:
            os.remove(path)
            data_path = os.path.splitext(path)[0] + '.csv'
            if os.path.isfile(data_path):
                os.remove(data_path)
        except:
            errors.append('There was an error removing file {}'.format(test_name))
    return errors


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


def _get_parsed_steps(function):
    """Get a list of parsed steps provided the code of a
    test function (setup, test or teardown)
    """
    steps = []
    code_lines = inspect.getsourcelines(function)[0]
    code_lines = [x.strip().replace('\n', '') for x in code_lines]
    code_lines.pop(0)
    for line in code_lines:
        if line != 'pass' and len(line):
            steps.append(_parse_step(line))
    return steps


def _format_page_object_string(pages):
    """Format page object string to store in test."""
    po_string = ''
    for page in pages:
        po_string = po_string + " '" + page + "',\n" + " " * 8
    po_string = "[{}]".format(po_string.strip()[:-1])
    return po_string


def _format_tags_string(tags):
    """Format tags string to store in test."""
    tags_string = ''
    for tag in tags:
        tags_string = tags_string + " '" + tag + "',"
    tags_string = "[{}]".format(tags_string.strip()[:-1])
    return tags_string


def _format_description(description):
    """Format description string to store in test."""
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
    """Format data string to store in test."""
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


class Test(BaseProjectElement):

    __test__ = False

    element_type = 'test'

    _module = None

    def get_module(self):
        if not self._module:
            self._module = self.module
        return self._module

    @property
    def description(self):
        return getattr(self.get_module(), 'description', '')

    @property
    def tags(self):
        return getattr(self.get_module(), 'tags', [])

    @property
    def pages(self):
        return getattr(self.get_module(), 'pages', [])

    @property
    def steps(self):
        steps = {
            'setup': [],
            'test': [],
            'teardown': []
        }

        setup_function = getattr(self.get_module(), 'setup', None)
        if setup_function:
            steps['setup'] = _get_parsed_steps(setup_function)
        else:
            steps['setup'] = []

        test_function = getattr(self.get_module(), 'test', None)
        if test_function:
            steps['test'] = _get_parsed_steps(test_function)
        else:
            steps['test'] = []

        teardown_function = getattr(self.get_module(), 'teardown', None)
        if teardown_function:
            steps['teardown'] = _get_parsed_steps(teardown_function)
        else:
            steps['teardown'] = []
        return steps

    @property
    def components(self):
        """Parse and return the components of a Test in
        the following structure:
          'description' :  string
          'pages' :        list of pages
          'tags'  :        list of tags
          'steps' :        step dictionary
            'setup' :      parsed setup steps
            'test' :       parsed test steps
            'teardown' :   parsed teardown steps
        """
        components = {
            'description': self.description,
            'pages': self.pages,
            'tags': self.tags,
            'steps': self.steps
        }
        return components
