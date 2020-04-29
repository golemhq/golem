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
        with open(base_file_path, 'a', encoding='utf-8') as base_file:
            base_file.write('{}')

    print('Project {} created'.format(project_name))


def delete_project(project_name):
    """Delete an entire project.
    DANGER
    """
    return file_manager.delete_directory(Project(project_name).path)


class ProjectFileTypes:
    TEST = 'test'
    PAGE = 'page'
    SUITE = 'suite'


class Project:

    file_types = ProjectFileTypes

    def __init__(self, project_name):
        self.name = project_name

    @property
    def path(self):
        return os.path.join(session.testdir, 'projects', self.name)

    def _file_tree(self, file_type):
        path = self.element_directory_path(file_type)
        return file_manager.generate_file_structure_dict(path)

    @property
    def test_tree(self):
        return self._file_tree(self.file_types.TEST)

    @property
    def page_tree(self):
        return self._file_tree(self.file_types.PAGE)

    @property
    def suite_tree(self):
        return self._file_tree(self.file_types.SUITE)

    def _file_list(self, file_type, directory=''):
        """List of files of `file_type`.
        Directory must be a relative path from the project element base folder
        """
        base_path = self.element_directory_path(file_type)
        path = os.path.join(base_path, directory)
        elements = file_manager.get_files_dot_path(path, extension='.py')
        if directory:
            dotpath = '.'.join(os.path.normpath(directory).split(os.sep))
            elements = ['.'.join([dotpath, x]) for x in elements]
        return elements

    def tests(self, directory=''):
        """List all tests in project or all tests in a subdirectory"""
        return self._file_list(self.file_types.TEST, directory)

    def pages(self, directory=''):
        """List all pages in project or all tests in a subdirectory"""
        return self._file_list(self.file_types.PAGE, directory)

    def suites(self, directory=''):
        """List all suites in project or all tests in a subdirectory"""
        return self._file_list(self.file_types.SUITE, directory)

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

    def element_directory_path(self, file_type):
        if file_type == self.file_types.TEST:
            return self.test_directory_path
        elif file_type == self.file_types.PAGE:
            return self.page_directory_path
        elif file_type == self.file_types.SUITE:
            return self.suite_directory_path
        else:
            raise ValueError()

    def create_packages_for_element(self, element_name, file_type):
        """Given an file name, creates its parent directories
        if they don't exist.

        For example:
          given file_name=my.folder.test_name,
          create packages: `my/` and `my/folder/`
        """
        base_path = self.element_directory_path(file_type)
        relpath = os.sep.join(element_name.split('.')[:-1])
        if relpath:
            file_manager.create_package_directories(base_path, relpath)

    def create_directories(self, dir_name, file_type):
        errors = validate_project_element_name(dir_name, isdir=True)
        if not errors:
            base_path = self.element_directory_path(file_type)
            relpath = os.sep.join(dir_name.split('.'))
            fullpath = os.path.join(base_path, relpath)
            if os.path.isdir(fullpath):
                errors.append('A directory with that name already exists')
            else:
                file_manager.create_package_directories(base_path, relpath)
        return errors

    def rename_directory(self, dir_name, new_dir_name, file_type):
        """Rename a directory inside tests, pages, or suites folder."""
        errors = validate_project_element_name(new_dir_name)
        if not errors:
            base_path = self.element_directory_path(file_type)
            src = os.sep.join(dir_name.split('.'))
            dst = os.sep.join(new_dir_name.split('.'))
            errors = file_manager.rename_directory(base_path, src, dst)
        return errors

    def delete_directory(self, dir_name, file_type):
        errors = []
        base_path = self.element_directory_path(file_type)
        relpath = os.sep.join(dir_name.split('.'))
        fullpath = os.path.join(base_path, relpath)
        if not os.path.isdir(fullpath):
            errors.append('Directory {} does not exist'.format(relpath))
        else:
            errors = file_manager.delete_directory(fullpath)
        return errors

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


def validate_project_element_name(name, isdir=False):
    """"Validate name for a test, page or suite (or folders).
    `name` must be a relative dot path from the base element folder.
    """
    errors = []
    parts = name.split('.')
    last_part = parts.pop()
    for part in parts:
        if len(part) == 0:
            errors.append('Directory name cannot be empty')
            break
        elif len(part) > 150:
            errors.append('Maximum name length is 150 characters')
            break
    if len(last_part) == 0:
        if isdir:
            errors.append('Folder name cannot be empty')
        else:
            errors.append('File name cannot be empty')
    elif len(last_part) > 150:
        errors.append('Maximum name length is 150 characters')
    for c in name:
        if not c.isalnum() and c not in ['_', '.']:
            errors.append('Only letters, numbers and underscores are allowed')
            break
    return errors


class BaseProjectElement:
    """Base class for project elements (test, page and suite)"""

    element_type = None

    def __init__(self, project, name):
        self.project = Project(project)
        self.name = name
        self.stem_name = name.split('.')[-1]
        self.filename = '{}.py'.format(self.stem_name)
        self.relpath = '{}.py'.format(self.name.replace('.', os.sep))

    @property
    def path(self):
        base_path = self.project.element_directory_path(self.element_type)
        return os.path.join(base_path, self.relpath)

    @property
    def dirname(self):
        return os.path.dirname(self.path)

    @property
    def exists(self):
        return os.path.isfile(self.path)

    @property
    def module(self):
        if self.exists:
            module_, _ = utils.import_module(self.path)
            return module_
        else:
            return None

    @property
    def code(self):
        """Code of the element as a string"""
        code = None
        if self.exists:
            with open(self.path, encoding='utf-8') as f:
                code = f.read()
        return code
