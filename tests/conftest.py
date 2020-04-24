import os
import shutil
import random
import string
from types import SimpleNamespace
from subprocess import Popen, PIPE, STDOUT

import pytest

from golem.cli import commands
from golem.core import settings_manager, suite, test, session, page, utils
from golem.report.execution_report import get_execution_data, suite_execution_path


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
        self.name = TestUtils.random_numeric_string(6, 'testdir_')
        self.path = os.path.join(self.basedir, self.name)
        self.settings = None
        session.testdir = self.path
        commands.createdirectory_command(self.path)

    def activate(self):
        session.testdir = self.path
        if self.settings is None:
            self.settings = settings_manager.get_global_settings()
        session.settings = self.settings
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
        self.name = TestUtils.random_numeric_string(6, 'project_')
        self.path = os.path.join(testdir_fixture.path, 'projects', self.name)
        self.settings = None
        session.testdir = self.testdir
        commands.createproject_command(self.name)

    def values(self):
        return self.testdir, self.name

    def activate(self):
        session.testdir = self.testdir
        if self.settings is None:
            self.settings = settings_manager.get_project_settings(self.name)
        session.settings = self.settings
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
        return filepath

    @staticmethod
    def random_string(length=10, prefix=''):
        random_str = (''.join(random.choice(string.ascii_lowercase)
                      for _ in range(length)))
        return prefix + random_str

    @staticmethod
    def random_email():
        local = TestUtils.random_string(10)
        domain = TestUtils.random_string(10)
        return '{}@{}.com'.format(local, domain)

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
            f.write('{{"{}": "{}"}}'.format(setting, setting_value))

    @staticmethod
    def create_test(project, name, content=None):
        if content is None:
            content = ('def test(data):\n'
                       '    print("hello")\n')
        test.create_test(project, name)
        test.edit_test_code(project, name, content, table_test_data=[])
        return test.Test(project, name).path

    @staticmethod
    def create_failure_test(project, name):
        content = ('def test(data):\n'
                   '    assert False\n')
        return TestUtils.create_test(project, name, content)

    @staticmethod
    def create_error_test(project, name):
        content = ('from golem import actions\n'
                   'def test(data):\n'
                   '    actions.error("error message")\n')
        return TestUtils.create_test(project, name, content)

    @staticmethod
    def create_code_error_test(project, name):
        content = ('def test(data):\n'
                   '    print("oops"\n')
        return TestUtils.create_test(project, name, content)

    @staticmethod
    def create_skip_test(project, name):
        content = ('skip = True\n' 
                   'def test(data):\n'
                   '    print("hello")\n')
        return TestUtils.create_test(project, name, content)

    @staticmethod
    def create_random_test(project):
        test_name = TestUtils.random_string(10)
        test.create_test(project, test_name)
        return test_name

    @staticmethod
    def create_suite(project, name, content=None, tests=None, processes=1, browsers=None,
                     environments=None, tags=None):
        browsers = browsers or []
        environments = environments or []
        tags = tags or []
        if content is None:
            suite.create_suite(project, name)
            suite.edit_suite(project, name, tests, processes, browsers, environments, tags)
        else:
            with open(suite.Suite(project, name).path, 'w+') as f:
                f.write(content)

    @staticmethod
    def create_page(project, page_name):
        page.create_page(project, page_name)

    @staticmethod
    def create_random_suite(project):
        suite_name = TestUtils.random_string()
        suite.create_suite(project, suite_name)
        return suite_name

    @staticmethod
    def create_random_page(project, code=None):
        page_name = TestUtils.random_string(10)
        page.create_page(project, page_name)
        if code is not None:
            page.edit_page_code(project, page_name, code)
        return page_name

    @staticmethod
    def _run_command(project_name, suite_name, timestamp=None):
        if not timestamp:
            timestamp = utils.get_timestamp()
        commands.run_command(project_name, suite_name, timestamp=timestamp)
        return timestamp

    @staticmethod
    def run_test(project_name, test_name, timestamp=None):
        return TestUtils._run_command(project_name, test_name, timestamp)

    @staticmethod
    def run_suite(project_name, suite_name, timestamp=None):
        return TestUtils._run_command(project_name, suite_name, timestamp)

    @staticmethod
    def execute_random_suite(project):
        """Create a random suite for project with one test.
        Execute the suite and return the execution data
        """
        test_name = TestUtils.random_string()
        tests = [test_name]
        for t in tests:
            TestUtils.create_test(project, name=t)
        suite_name = TestUtils.random_string()
        TestUtils.create_suite(project, name=suite_name, tests=tests)
        execution = TestUtils.execute_suite(project, suite_name)
        execution['tests'] = tests
        return execution

    @staticmethod
    def execute_suite(project, suite_name, timestamp=None, ignore_sys_exit=False):
        if not timestamp:
            timestamp = utils.get_timestamp()
        try:
            timestamp = TestUtils.run_suite(project, suite_name, timestamp)
        except SystemExit as e:
            if not ignore_sys_exit:
                raise e
        exec_data = get_execution_data(project=project, suite=suite_name, execution=timestamp)
        exec_dir = suite_execution_path(project, suite_name, timestamp)
        return {
            'exec_dir': exec_dir,
            'report_path': os.path.join(exec_dir, 'report.json'),
            'suite_name': suite_name,
            'timestamp': timestamp,
            'exec_data': exec_data
        }


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
