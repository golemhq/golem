import os

from golem.core import session, file_manager, settings_manager, utils


def create_project(project_name):
    project = Project(project_name)
    file_manager.create_directory(path=project.path, add_init=True)
    file_manager.create_directory(path=project.test_directory_path, add_init=True)
    file_manager.create_directory(path=project.page_directory_path, add_init=True)
    file_manager.create_directory(path=project.suite_directory_path, add_init=True)
    file_manager.create_directory(path=project.report_directory_path, add_init=True)
    extend_path = os.path.join(project.path, 'extend.py')
    open(extend_path, 'a').close()

    settings_manager.create_project_settings_file(project_name)

    for project_base_file in ('environments.json', 'secrets.json'):
        base_file_path = os.path.join(project.path, project_base_file)
        with open(base_file_path, 'a') as base_file:
            base_file.write('{}')

    print('Project {} created'.format(project_name))


class ProjectElementTypes:
    TEST = 'test'
    PAGE = 'page'
    SUITE = 'suite'


class Project:

    element_types = ProjectElementTypes

    def __init__(self, project_name):
        self.name = project_name

    @property
    def path(self):
        return os.path.join(session.testdir, 'projects', self.name)

    @property
    def test_tree(self):
        path = os.path.join(self.path, 'tests')
        return file_manager.generate_file_structure_dict(path)

    @property
    def page_tree(self):
        path = os.path.join(self.path, 'pages')
        return file_manager.generate_file_structure_dict(path)

    @property
    def suite_tree(self):
        path = os.path.join(self.path, 'suites')
        return file_manager.generate_file_structure_dict(path)

    def _element_list(self, element_type, directory=''):
        """List of elements of `element_type`.
        Directory must be a relative path from the project element base folder
        """
        base_path = self.element_directory_path(element_type)
        path = os.path.join(base_path, directory)
        elements = file_manager.get_files_dot_path(path, extension='.py')
        if directory:
            dotpath = '.'.join(os.path.normpath(directory).split(os.sep))
            elements = ['.'.join([dotpath, x]) for x in elements]
        return elements

    def tests(self, directory=''):
        """List all tests in project or all tests in a subdirectory"""
        return self._element_list('test', directory)

    def pages(self, directory=''):
        """List all pages in project or all tests in a subdirectory"""
        return self._element_list('page', directory)

    def suites(self, directory=''):
        """List all suites in project or all tests in a subdirectory"""
        return self._element_list('suite', directory)

    @property
    def has_tests(self):
        return self.tests() != []

    @property
    def test_directory_path(self):
        return os.path.join(self.path, 'tests')

    @property
    def suite_directory_path(self):
        return os.path.join(self.path, 'suites')

    @property
    def page_directory_path(self):
        return os.path.join(self.path, 'pages')

    @property
    def report_directory_path(self):
        return os.path.join(self.path, 'reports')

    def element_directory_path(self, element_type):
        if element_type == self.element_types.TEST:
            return self.test_directory_path
        elif element_type == self.element_types.PAGE:
            return self.page_directory_path
        elif element_type == self.element_types.SUITE:
            return self.suite_directory_path
        else:
            raise ValueError()

    def create_packages_for_element(self, element_name, element_type):
        """Given an element name, creates its parent directories
        if they don't exist.

        For example:
          given element_name=my.folder.test_name,
          create packages: `my/` and `my/folder/`
        """
        base_path = self.element_directory_path(element_type)
        relpath = os.sep.join(element_name.split('.')[:-1])
        if relpath:
            file_manager.create_package_directories(base_path, relpath)

    def create_directories(self, dir_name, dir_type):
        errors = validate_project_element_name(dir_name)
        if not errors:
            base_path = self.element_directory_path(dir_type)
            relpath = os.sep.join(dir_name.split('.'))
            fullpath = os.path.join(base_path, relpath)
            if os.path.isdir(fullpath):
                errors.append('A directory with that name already exists')
            else:
                file_manager.create_package_directories(base_path, relpath)
        return errors

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


def validate_project_element_name(name):
    """"Validate name for a test, page or suite.
    `name` must be a relative dot path from the base element folder.
    """
    errors = []
    parts = name.split('.')
    last_part = parts.pop()
    for part in parts:
        if len(part) == 0:
            errors.append('Directory name cannot be empty')
            break
    if len(last_part) == 0:
        errors.append('File name cannot be empty')
    for c in name:
        if not c.isalnum() and c not in ['_', '.']:
            errors.append('Only letters, numbers and underscores are allowed')
            break
    return errors


class BaseProjectElement:
    """Base class for project elements (test, page and suite)"""

    element_type = None

    def __init__(self, project, name):
        self.project = project
        self.name = name

    @property
    def path(self):
        base_path = Project(self.project).element_directory_path(self.element_type)
        return os.path.join(base_path, self.name.replace('.', os.sep) + '.py')

    @property
    def exists(self):
        return os.path.isfile(self.path)

    @property
    def module(self):
        module_, _ = utils.import_module(self.path)
        return module_

    @property
    def code(self):
        """Code of the element as a string"""
        code = ''
        if os.path.isfile(self.path):
            with open(self.path) as f:
                code = f.read()
        return code
