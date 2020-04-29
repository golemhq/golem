"""Methods for dealing with suite modules
Suites are modules located inside the /suites/ directory
"""
import os
import shutil

from golem.core import file_manager
from golem.core.project import Project, validate_project_element_name, BaseProjectElement


def create_suite(project_name, suite_name):
    suite_content = ('\n'
                     'browsers = []\n\n'
                     'environments = []\n\n'
                     'processes = 1\n\n'
                     'tests = []\n')
    errors = []
    project = Project(project_name)
    if suite_name in project.suites():
        errors.append('A suite with that name already exists')
    else:
        errors = validate_project_element_name(suite_name)
    if not errors:
        project.create_packages_for_element(suite_name, project.file_types.SUITE)
        with open(Suite(project_name, suite_name).path, 'w', encoding='utf-8') as f:
            f.write(suite_content)
        print('Suite {} created for project {}'.format(suite_name, project_name))
    return errors


def rename_suite(project, suite_name, new_suite_name):
    errors = []
    project_obj = Project(project)
    if suite_name not in project_obj.suites():
        errors.append('Suite {} does not exist'.format(suite_name))
    else:
        errors = validate_project_element_name(new_suite_name)
    if not errors:
        old_path = Suite(project, suite_name).path
        new_path = Suite(project, new_suite_name).path
        project_obj.create_packages_for_element(new_suite_name, Project.file_types.SUITE)
        errors = file_manager.rename_file(old_path, new_path)
    return errors


def duplicate_suite(project, name, new_name):
    errors = []
    old_path = Suite(project, name).path
    new_path = Suite(project, new_name).path
    if name == new_name:
        errors.append('New suite name cannot be the same as the original')
    elif not os.path.isfile(old_path):
        errors.append('Suite {} does not exist'.format(name))
    elif os.path.isfile(new_path):
        errors.append('A suite with that name already exists')
    else:
        errors = validate_project_element_name(new_name)
    if not errors:
        try:
            Project(project).create_packages_for_element(new_name, Project.file_types.SUITE)
            shutil.copyfile(old_path, new_path)
        except:
            errors.append('There was an error creating the new suite')
    return errors


def edit_suite(project, suite_name, tests, processes, browsers, environments, tags):
    with open(Suite(project, suite_name).path, 'w', encoding='utf-8') as f:
        f.write('\n\n')
        f.write('browsers = {}\n'.format(_format_list_items(browsers)))
        f.write('\n')
        f.write('environments = {}\n'.format(_format_list_items(environments)))
        f.write('\n')
        if tags:
            f.write('tags = {}\n'.format(_format_list_items(tags)))
            f.write('\n')
        if not processes:
            processes = 1
        f.write('processes = {}'.format(processes))
        f.write('\n\n')
        f.write('tests = {}\n'.format(_format_list_items(tests)))


def delete_suite(project, suite):
    errors = []
    path = Suite(project, suite).path
    if not os.path.isfile(path):
        errors.append('Suite {} does not exist'.format(suite))
    else:
        try:
            os.remove(path)
        except:
            errors.append('There was an error removing file {}'.format(suite))
    return errors


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


class Suite(BaseProjectElement):

    element_type = 'suite'

    _module = None

    def get_module(self):
        if not self._module:
            self._module = self.module
        return self._module

    @property
    def processes(self):
        return getattr(self.get_module(), 'processes', 1)

    @property
    def environments(self):
        return getattr(self.get_module(), 'environments', [])

    @property
    def browsers(self):
        return getattr(self.get_module(), 'browsers', [])

    @property
    def tags(self):
        return getattr(self.get_module(), 'tags', [])

    @property
    def tests(self):
        """Return a list with all the test cases in the suite"""
        # TODO should use glob
        tests = []
        module = self.get_module()

        if not hasattr(module, 'tests'):
            return tests

        if '*' in module.tests:
            tests = self.project.tests()
        else:
            for test in module.tests:
                if test.endswith('.*'):
                    this_dir = test[:-2]
                    path = os.path.join(self.project.test_directory_path,
                                        os.sep.join(this_dir.split('.')))
                    this_dir_tests = file_manager.get_files_dot_path(path, extension='.py')
                    this_dir_tests = ['{}.{}'.format(this_dir, x) for x in this_dir_tests]
                    tests = tests + this_dir_tests
                else:
                    tests.append(test)
        return tests
