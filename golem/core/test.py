import os
import shutil

from golem.core import file_manager, settings_manager
from golem.core import test_data as test_data_module
from golem.core.project import Project, validate_project_element_name, BaseProjectElement
from golem.core import test_parser


def create_test(project_name, test_name):
    test_content = (
        "\n"
        "description = ''\n\n"
        "tags = []\n\n"
        "pages = []\n\n\n"
        "def setup(data):\n"
        "    pass\n\n\n"
        "def test(data):\n"
        "    pass\n\n\n"
        "def teardown(data):\n"
        "    pass\n\n")
    errors = []
    project = Project(project_name)
    if test_name in project.tests():
        errors.append('A test with that name already exists')
    else:
        errors = validate_project_element_name(test_name)
    if not errors:
        project.create_packages_for_element(test_name, project.file_types.TEST)
        path = Test(project_name, test_name).path
        with open(path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        print('Test {} created for project {}'.format(test_name, project_name))
    return errors


def rename_test(project_name, test_name, new_test_name):
    errors = []
    project = Project(project_name)
    if test_name not in project.tests():
        errors.append('Test {} does not exist'.format(test_name))
    else:
        errors = validate_project_element_name(new_test_name)
    if not errors:
        old_path = Test(project_name, test_name).path
        new_path = Test(project_name, new_test_name).path
        project.create_packages_for_element(new_test_name, project.file_types.TEST)
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
            Project(project).create_packages_for_element(new_name, Project.file_types.TEST)
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


def edit_test(project, test_name, description, pages, steps, test_data, tags, skip=False):
    """Save test contents to file"""

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

    def _format_tags_string(tags):
        tags_string = ''
        for tag in tags:
            tags_string = tags_string + " '" + tag + "',"
        tags_string = "[{}]".format(tags_string.strip()[:-1])
        return tags_string

    def _format_page_string(pages):
        """Format page object string to store in test."""
        po_string = ''
        for page in pages:
            po_string = po_string + " '" + page + "',\n" + " " * 8
        po_string = "[{}]".format(po_string.strip()[:-1])
        return po_string

    def _format_data(test_data):
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

    def _format_steps(steps):
        step_str = ''
        for step in steps:
            if step['type'] == 'function-call':
                step_action = step['action'].replace(' ', '_')
                param_str = ', '.join(step['parameters'])
                step_str += '    {0}({1})\n'.format(step_action, param_str)
            else:
                lines = step['code'].splitlines()
                for line in lines:
                    step_str += '    {}\n'.format(line)
        return step_str

    path = Test(project, test_name).path
    settings = settings_manager.get_project_settings(project)
    with open(path, 'w', encoding='utf-8') as f:
        if not settings['implicit_actions_import']:
            f.write('from golem import actions\n\n')
        if not settings['implicit_page_import']:
            for page in pages:
                split = page.split('.')
                top = split.pop()
                parents = '.'.join(split)
                parents = '.{}'.format(parents) if parents else ''
                f.write('from projects.{}.pages{} import {}\n'.format(project, parents, top))
            f.write('\n')
        f.write('\n')
        f.write(_format_description(description))
        f.write('\n')
        f.write('tags = {}\n'.format(_format_tags_string(tags)))
        f.write('\n')
        if settings['implicit_page_import']:
            f.write('pages = {}\n'.format(_format_page_string(pages)))
            f.write('\n')
        if settings['test_data'] == 'infile':
            if test_data:
                f.write('data = {}'.format(_format_data(test_data)))
                test_data_module.remove_csv_if_exists(project, test_name)
        else:
            test_data_module.save_external_test_data_file(project, test_name, test_data)
        if skip:
            if type(skip) is str:
                skip = "'{}'".format(skip)
            f.write('skip = {}\n\n'.format(skip))
        f.write('\n')
        f.write('def setup(data):\n')
        if steps['setup']:
            f.write(_format_steps(steps['setup']))
        else:
            f.write('    pass\n')
        f.write('\n\n')
        f.write('def test(data):\n')
        if steps['test']:
            f.write(_format_steps(steps['test']))
        else:
            f.write('    pass\n')
        f.write('\n\n')
        f.write('def teardown(data):\n')
        if steps['teardown']:
            f.write(_format_steps(steps['teardown']))
        else:
            f.write('    pass\n')


def edit_test_code(project, test_name, content, table_test_data):
    path = Test(project, test_name).path
    with open(path, 'w', encoding='utf-8') as f:
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


class Test(BaseProjectElement):

    __test__ = False

    element_type = 'test'

    _module = None

    def get_module(self):
        if self._module is None:
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
        page_list = getattr(self.get_module(), 'pages', [])
        imported_pages = test_parser.parse_imported_pages(self.code)
        return page_list + imported_pages

    @property
    def steps(self):
        steps = {
            'setup': [],
            'test': [],
            'teardown': []
        }

        setup_function = getattr(self.get_module(), 'setup', None)
        if setup_function:
            steps['setup'] = test_parser.parse_function_steps(setup_function)
        else:
            steps['setup'] = []

        test_function = getattr(self.get_module(), 'test', None)
        if test_function:
            steps['test'] = test_parser.parse_function_steps(test_function)
        else:
            steps['test'] = []

        teardown_function = getattr(self.get_module(), 'teardown', None)
        if teardown_function:
            steps['teardown'] = test_parser.parse_function_steps(teardown_function)
        else:
            steps['teardown'] = []
        return steps

    @property
    def skip(self):
        return getattr(self.get_module(), 'skip', False)

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
            'steps': self.steps,
            'skip': self.skip
        }
        return components
