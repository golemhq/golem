import os
import shutil
import random
import string
from types import SimpleNamespace
from subprocess import Popen, PIPE, STDOUT

import pytest

from golem.cli import commands
from golem.core import test_execution, settings_manager, suite, test_case, utils


# FIXTURES

BASEDIR = None


def get_basedir():
    global BASEDIR
    if not BASEDIR:
        BASEDIR = os.getcwd()
    return BASEDIR


@pytest.fixture(scope="function")
def dir_function():
    """An empty directory"""
    basedir = get_basedir()
    dirname = TestUtils().random_string(4, 'tempdir_')
    path = os.path.join(basedir, dirname)
    os.mkdir(path)
    os.chdir(path)
    directory = SimpleNamespace(name=dirname, path=path, basedir=basedir)
    yield directory
    os.chdir(basedir)
    shutil.rmtree(dirname, ignore_errors=True)


class TestDirectory:
    """Creates and and removes a test directory"""

    def __init__(self, basedir):
        self.basedir = basedir
        self.name = TestUtils.random_string(4, 'testdir_')
        self.path = os.path.join(self.basedir, self.name)
        self.settings = None
        os.chdir(self.basedir)
        commands.createdirectory_command(self.name)

    def activate(self):
        if self.settings is None:
            self.settings = settings_manager.get_global_settings(self.path)
        test_execution.root_path = self.path
        test_execution.settings = self.settings
        return self.path

    def remove(self):
        os.chdir(self.basedir)
        shutil.rmtree(self.name, ignore_errors=True)


@pytest.fixture(scope="session")
def testdir_session():
    """A test directory with scope session"""
    basedir = get_basedir()
    testdir = TestDirectory(basedir)
    yield testdir
    testdir.remove()


@pytest.fixture(scope="class")
def testdir_class():
    """A test directory with scope class"""
    basedir = get_basedir()
    testdir = TestDirectory(basedir)
    yield testdir
    testdir.remove()


@pytest.fixture(scope="function")
def testdir_function():
    """A test directory with scope function"""
    basedir = get_basedir()
    testdir = TestDirectory(basedir)
    yield testdir
    testdir.remove()


class Project:
    """Creates and removes a project inside a test directory"""

    def __init__(self, testdir_fixture):
        self.testdir_fixture = testdir_fixture
        self.testdir = testdir_fixture.path
        self.name = TestUtils.random_string(4, 'project_')
        self.path = os.path.join(testdir_fixture.path, 'projects', self.name)
        self.settings = None
        os.chdir(self.testdir)
        test_execution.root_path = self.testdir
        commands.createproject_command(self.name)

    def values(self):
        return self.testdir, self.name

    def activate(self):
        if self.settings is None:
            self.settings = settings_manager.get_project_settings(self.testdir, self.name)
        test_execution.root_path = self.testdir
        test_execution.settings = self.settings
        return self.values()

    def remove(self):
        shutil.rmtree(self.path, ignore_errors=True)


@pytest.mark.usefixtures("testdir_session")
@pytest.fixture(scope="session")
def project_session(testdir_session):
    """A project with scope session"""
    project = Project(testdir_session)
    yield project
    project.remove()


@pytest.mark.usefixtures("testdir_session")
@pytest.fixture(scope="class")
def project_class(testdir_session):
    """A project with scope class inside
    a test directory with scope session.
    """
    project = Project(testdir_session)
    yield project
    project.remove()


@pytest.mark.usefixtures("testdir_session")
@pytest.fixture(scope="function")
def project_function(testdir_session):
    """A project with scope function inside
    a test directory with scope session.
    """
    project = Project(testdir_session)
    yield project
    project.remove()


@pytest.mark.usefixtures("testdir_function")
@pytest.fixture(scope="function")
def project_function_clean(testdir_function):
    """A project with scope function inside
    a session with scope function.
    """
    project = Project(testdir_function)
    yield project
    project.remove()


@pytest.fixture(scope="session")
def test_utils():    
    yield TestUtils


# TEST UTILS   

class TestUtils:

    @staticmethod
    def create_empty_file(path, filename):
        filepath = os.path.join(path, filename)
        os.makedirs(path, exist_ok=True)
        open(filepath, 'w+').close()

    @staticmethod
    def random_string(length, prefix=''):
        random_str = (''.join(random.choice(string.ascii_lowercase)
                      for _ in range(length)))
        return prefix + random_str

    @staticmethod
    def random_numeric_string(length, prefix=''):
        random_str = ''.join(random.choice(string.digits) for _ in range(length))
        return prefix + random_str

    @staticmethod
    def run_command(cmd):
        output = ''
        p = Popen(cmd, stdout=PIPE, stderr=STDOUT, bufsize=0,
                  shell=True, universal_newlines=True)
        output = p.stdout.read()
        if len(output) > 1 and output[-1] == '\n':
            output = output[:-1]
        return output

    @staticmethod
    def set_project_setting(testdir, setting, setting_value):
        setting_path = os.path.join(testdir, 'settings.json')
        with open(setting_path, 'w') as f:
            f.write('{{"{}": "{}"\}}'.format(setting, setting_value))

    @staticmethod
    def create_test(testdir, project, parents, name, content=None):
        if content is None:
            content = ('def test(data):\n'
                       '    print("hello")\n')
        test_case.new_test_case(testdir, project, parents, name)
        path = os.path.join(testdir, 'projects', project, 'tests',
                            os.sep.join(parents), name + '.py')
        with open(path, 'w+') as f:
            f.write(content)
        return path

    @staticmethod
    def create_suite(testdir, project, name, content=None, tests=None,
                     processes=1, browsers=None, environments=None, tags=None):
        browsers = browsers or []
        environments = environments or []
        tags = tags or []
        suite_name, parents = utils.separate_file_from_parents(name)
        if content is None:
            suite.new_suite(testdir, project, parents, suite_name)
            suite.save_suite(testdir, project, name, tests, processes, browsers,
                             environments, tags)
        else:
            path = os.path.join(testdir, 'projects', project, 'suites',
                                os.sep.join(parents), name + '.py')
            with open(path, 'w+') as f:
                f.write(content)


def pytest_addoption(parser):
    parser.addoption('--integration', action='store_true', help='run integration tests only')
    parser.addoption('--fast', action='store_true', help='run integration tests only')
    parser.addoption('--all', action='store_true', help='run all tests')


def pytest_runtest_setup(item):
    """Filter tests

    '' (no option): Run all non integration tests
    '--integration' Run integration tests only
    '--fast':       Run fast tests only
    '--all':        Run all tests
    """
    if item.config.getoption('--all'):
        pass  # run all tests
    else:
        if item.config.getoption('--integration'):
            # skip non integration tests
            if 'integration' not in item.keywords:
                pytest.skip('skipping non integration test')
        else:
            # skip integration tests
            if 'integration' in item.keywords:
                pytest.skip('skipping integration test')
        if item.config.getoption('--fast'):
            # skip slow test
            if 'slow' in item.keywords:
                pytest.skip('skipping slow test')
