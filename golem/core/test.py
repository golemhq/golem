import os
import shutil

from golem.core import file_manager, settings_manager
from golem.core import test_data as test_data_module
from golem.core.project import Project, validate_project_element_name, BaseProjectElement
from golem.core import test_parser
from golem.core import parsing_utils


def create_test(project_name, test_name):
    test_content = (
        '\n'
        'def test(data):\n'
        '    pass\n'
    )
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
        print(f'Test {test_name} created for project {project_name}')
    return errors


def rename_test(project_name, test_name, new_test_name):
    errors = []
    project = Project(project_name)
    if test_name not in project.tests():
        errors.append(f'Test {test_name} does not exist')
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
        errors.append(f'Test {name} does not exist')
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
            formatted_description = formatted_description + '\'\'\''
        else:
            formatted_description = f"description = '{description}'"
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
                result += f"        '{key}': {value},\n"
            result += '    },\n'
        result += ']'
        return result

    def _format_steps(steps):
        step_lines = []
        for step in steps:
            if step['type'] == 'function-call':
                step_action = step['action'].replace(' ', '_')
                param_str = ', '.join(step['parameters'])
                step_lines.append(f'    {step_action}({param_str})')
            else:
                lines = step['code'].splitlines()
                for line in lines:
                    step_lines.append(f'    {line}')
        return '\n'.join(step_lines)

    def _print_extra_blank_line():
        nonlocal extra_blank_line
        if extra_blank_line:
            test_.append('')
            extra_blank_line = False

    def _order_hooks(test_hooks):
        """Put the test hooks in a predefined order"""
        ordered = {}
        order_list = ['before_test', 'setup', 'before_each', 'after_each', 'after_test', 'teardown']
        for hook_name in order_list:
            if hook_name in test_hooks:
                ordered[hook_name] = test_hooks[hook_name]
        return ordered

    path = Test(project, test_name).path
    settings = settings_manager.get_project_settings(project)

    test_ = []

    if not settings['implicit_actions_import']:
        test_.append('from golem import actions')
    if not settings['implicit_page_import']:
        if pages and not settings['implicit_actions_import']:
            test_.append('')
        for page in pages:
            split = page.split('.')
            top = split.pop()
            parents = '.'.join(split)
            parents = f'.{parents}' if parents else ''
            test_.append(f'from projects.{project}.pages{parents} import {top}')

    extra_blank_line = False
    if not settings['implicit_actions_import'] or not settings['implicit_page_import']:
        extra_blank_line = True

    if description:
        _print_extra_blank_line()
        test_.append('')
        test_.append(_format_description(description))

    if tags:
        _print_extra_blank_line()
        test_.append('')
        test_.append(f'tags = {_format_tags_string(tags)}')

    if pages and settings['implicit_page_import']:
        _print_extra_blank_line()
        test_.append('')
        test_.append(f'pages = {_format_page_string(pages)}')

    if test_data['csv'] is not None:
        test_data_module.save_csv_test_data(project, test_name, test_data['csv'])
    else:
        test_data_module.remove_csv_if_present(project, test_name)

    if test_data['json'] is not None and test_data['json'].strip():
        test_data_module.save_json_test_data(project, test_name, test_data['json'])
    else:
        test_data_module.remove_json_data_if_present(project, test_name)

    if test_data['internal'] is not None and test_data['internal'].strip():
        _print_extra_blank_line()
        test_.append('')
        test_.append(test_data['internal'])

    if skip:
        _print_extra_blank_line()
        test_.append('')
        if type(skip) is str:
            skip = f"'{skip}'"
        test_.append(f'skip = {skip}')

    if steps['hooks']:
        ordered_hooks = _order_hooks(steps['hooks'])
        for hook, hook_steps in ordered_hooks.items():
            if hook_steps:
                test_.append('')
                test_.append('')
                test_.append(f'def {hook}(data):')
                test_.append(_format_steps(hook_steps))

    for test_function_name, test_function_steps in steps['tests'].items():
        test_.append('')
        test_.append('')
        test_.append(f'def {test_function_name}(data):')
        if test_function_steps:
            test_.append(_format_steps(test_function_steps))
        else:
            test_.append('    pass')

    test_.append('')

    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(test_))


def edit_test_code(project, test_name, content, test_data=None):
    path = Test(project, test_name).path
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    # save test data
    if test_data is not None:
        if test_data['csv'] is not None:
            test_data_module.save_csv_test_data(project, test_name, test_data['csv'])
            test_data_module.remove_json_data_if_present(project, test_name)
        else:
            test_data_module.remove_csv_if_present(project, test_name)

        if test_data['json'] is not None and test_data['json'].strip():
            test_data_module.save_json_test_data(project, test_name, test_data['json'])
        else:
            test_data_module.remove_json_data_if_present(project, test_name)


def delete_test(project, test_name):
    errors = []
    path = Test(project, test_name).path
    if not os.path.isfile(path):
        errors.append(f'Test {test_name} does not exist')
    else:
        try:
            os.remove(path)
            data_path = os.path.splitext(path)[0] + '.csv'
            if os.path.isfile(data_path):
                os.remove(data_path)
        except:
            errors.append(f'There was an error removing file {test_name}')
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
    def test_functions(self):
        """Dictionary of parsed steps of each test function"""
        tests = {}
        test_function_list = self.test_function_list
        for test_function in test_function_list:
            function = getattr(self.get_module(), test_function)
            tests[test_function] = test_parser.parse_function_steps(function)
        return tests

    @property
    def test_function_list(self):
        """List of test functions.
        Test functions are functions defined inside this test file that start with 'test'
        """
        ast_module_node = parsing_utils.ast_parse_file(self.path)
        local_function_names = parsing_utils.top_level_functions(ast_module_node)
        return [f for f in local_function_names if f.startswith('test')]

    @property
    def test_hooks(self):
        """Dictionary of parsed steps of each test hook function"""
        hooks = {}
        test_hooks = self.test_hook_list
        for hook_name in test_hooks:
            h = getattr(self.get_module(), hook_name)
            # TODO setup / teardown are deprecated, returned as before_test/after_test
            if hook_name == 'setup':
                hook_name = 'before_test'
            if hook_name == 'teardown':
                hook_name = 'after_test'
            hooks[hook_name] = test_parser.parse_function_steps(h)

        from collections import OrderedDict
        return OrderedDict(hooks)

    @property
    def test_hook_list(self):
        """List of test hook functions"""
        ast_module_node = parsing_utils.ast_parse_file(self.path)
        local_function_names = parsing_utils.top_level_functions(ast_module_node)
        test_hook_names = ['setup', 'teardown', 'before_test', 'before_each', 'after_each', 'after_test']
        test_hooks = [f for f in local_function_names if f in test_hook_names]
        # TODO: setup / teardown are deprecated
        if 'setup' in test_hooks and 'before_test' in test_hooks:
            test_hooks.remove('setup')
        if 'teardown' in test_hooks and 'after_test' in test_hooks:
            test_hooks.remove('teardown')
        return test_hooks

    @property
    def skip(self):
        return getattr(self.get_module(), 'skip', False)

    @property
    def components(self):
        """Parse and return the components of a Test in
        the following structure:
          'description' :       string
          'pages' :             list of pages
          'tags' :              list of tags
          'skip' :              list of tags
          'setup_steps' :       parsed setup function
          'teardown_steps' :    parsed teardown function
          'test_functions' :    dictionary of test functions
            '<test_function>' : parsed test function steps
          'test_function_list': list of test function names
          'code'
        """
        components = {
            'description': self.description,
            'pages': self.pages,
            'tags': self.tags,
            'skip': self.skip,
            'test_functions': self.test_functions,
            'test_function_list': self.test_function_list,
            'test_hooks': self.test_hooks,
            'test_hook_list': self.test_hook_list,
            'code': self.code
        }
        return components
