import os

from golem.core import session, file_manager, settings_manager


def create_project(project):
    project_path = os.path.join(session.testdir, 'projects', project)
    file_manager.create_directory(path=project_path, add_init=True)
    file_manager.create_directory(path_list=[project_path, 'pages'], add_init=True)
    file_manager.create_directory(path_list=[project_path, 'reports'], add_init=False)
    file_manager.create_directory(path_list=[project_path, 'tests'], add_init=True)
    file_manager.create_directory(path_list=[project_path, 'suites'], add_init=True)
    extend_path = os.path.join(project_path, 'extend.py')
    open(extend_path, 'a').close()

    settings_manager.create_project_settings_file(project)

    for project_base_file in ('environments.json', 'secrets.json'):
        base_file_path = os.path.join(project_path, project_base_file)
        with open(base_file_path, 'a') as base_file:
            base_file.write('{}')

    print('Project {} created'.format(project))


class Project:

    def __init__(self, project_name):
        self.project_name = project_name

    @property
    def path(self):
        return os.path.join(session.testdir, 'projects', self.project_name)

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

    def tests(self, directory=''):
        """The list of tests of the project inside the `tests` folder
        or a subdirectory.
        Directory should be a relative path from the project `tests` folder
        """
        path = os.path.join(self.path, 'tests', directory)
        tests = file_manager.get_files_dot_path(path, extension='.py')
        if directory:
            dotpath = '.'.join(os.path.normpath(directory).split(os.sep))
            tests = ['.'.join([dotpath, x]) for x in tests]
        return tests

    @property
    def has_tests(self):
        return self.tests() != []

    def __repr__(self):
        return self.project_name

    def __str__(self):
        return self.project_name
