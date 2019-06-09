import os

from golem.core import test_directory
from golem.core.project import create_project


class TestCreateTestDirectory:

    def test_new_directory_contents(self, dir_function, test_utils):
        name = test_utils.random_string(10)
        os.chdir(dir_function.path)
        testdir = os.path.join(dir_function.path, name)
        test_directory.create_test_directory(testdir)
        listdir = os.listdir(testdir)
        files = [name for name in listdir if os.path.isfile(os.path.join(testdir, name))]
        dirs = [name for name in listdir if os.path.isdir(os.path.join(testdir, name))]
        if '.DS_Store' in files:
            files.remove('.DS_Store')
        assert len(files) == 4
        # verify files
        assert '__init__.py' in files
        assert 'settings.json' in files
        assert 'users.json' in files
        assert '.golem' in files
        # verify directories
        assert len(dirs) == 2
        # verify the test dir contains the correct directories
        assert 'projects' in dirs
        assert 'drivers' in dirs


class TestCreateTestdirGolemFile:

    def test_create_testdir_golem_file(self, dir_function):
        testdir = dir_function.path
        test_directory.create_testdir_golem_file(testdir)
        golem_file_path = os.path.join(testdir, '.golem')
        assert os.path.isfile(golem_file_path)
        with open(golem_file_path) as f:
            lines = f.readlines()
            assert lines[0] == '[gui]\n'
            assert lines[1].startswith('secret_key = ')


class TestGetProjects:

    def test_get_projects(self, testdir_function):
        testdir_function.activate()
        create_project('project1')
        create_project('project2')
        projects = test_directory.get_projects()
        assert projects.sort() == ['project1', 'project2'].sort()

    def test_get_projects_no_project(self, testdir_function):
        testdir_function.activate()
        projects = test_directory.get_projects()
        assert projects == []


class TestProjectExists:

    def test_project_exists(self, testdir_session, test_utils):
        testdir_session.activate()
        project = test_utils.random_string(10)
        assert not test_directory.project_exists(project)
        create_project(project)
        assert test_directory.project_exists(project)


class TestIsValidTestDirectory:

    def test_is_valid_test_directory(self, dir_function):
        path = dir_function.path
        assert not test_directory.is_valid_test_directory(path)
        test_directory.create_testdir_golem_file(path)
        assert test_directory.is_valid_test_directory(path)
