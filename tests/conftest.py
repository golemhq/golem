import os
import shutil
import random
import string
from subprocess import call, Popen, PIPE, STDOUT

import pytest

from golem.cli import commands
from golem.core import test_execution


# FIXTURES

BASE_DIR = None

session_testdir = {}

session_project = {}


def get_base_dir():
    global BASE_DIR
    if not BASE_DIR:
        BASE_DIR = os.getcwd()
    return BASE_DIR


@pytest.fixture(scope="function")
def dir_function():
    base_dir = get_base_dir()
    dirname = Test_utils().random_string(4, 'tempdir_')
    path = os.path.join(base_dir, dirname)
    os.mkdir(path)
    os.chdir(path)
    yield {
        'name': dirname,
        'path': path,
        'base_path': base_dir
    }
    os.chdir(base_dir)
    shutil.rmtree(dirname, ignore_errors=True)


def _create_testdir(base_dir):
    base_dir = get_base_dir()
    os.chdir(base_dir)
    testdir_name = Test_utils.random_string(4, 'testdir_')
    full_path = os.path.join(base_dir, testdir_name)
    commands.createdirectory_command(testdir_name)
    return testdir_name, full_path


@pytest.fixture(scope="session")
def testdir_session():
    base_dir = get_base_dir()
    global session_testdir
    if not session_testdir:
        testdir_name, full_path = _create_testdir(base_dir)
        session_testdir = {
            'path': full_path,
            'base_path': base_dir,
            'name': testdir_name}
    yield session_testdir
    os.chdir(base_dir)
    shutil.rmtree(session_testdir['name'], ignore_errors=True)


@pytest.fixture(scope="class")   
def testdir_class():
    base_dir = get_base_dir()
    testdir_name, full_path = _create_testdir(base_dir)
    yield {
            'path': full_path,
            'base_path': base_dir,
            'name': testdir_name}
    os.chdir(base_dir)
    shutil.rmtree(testdir_name, ignore_errors=True)


@pytest.fixture(scope="function")   
def testdir_function():
    base_dir = get_base_dir()
    testdir_name, full_path = _create_testdir(base_dir)
    yield {
            'path': full_path,
            'base_path': base_dir,
            'name': testdir_name}
    os.chdir(base_dir)
    shutil.rmtree(full_path, ignore_errors=True)


def _create_project(testdir, project_name):
    os.chdir(testdir)
    test_execution.root_path = testdir
    commands.createproject_command(project_name)


@pytest.mark.usefixtures("testdir_session")
@pytest.fixture(scope="session")
def project_session(testdir_session):
    global session_project
    if not session_project:
        project_name = Test_utils.random_string(4, 'project_')
        _create_project(testdir_session['path'], project_name)
        session_project = {
            'name': project_name,
            'testdir_fixture': testdir_session,
            'testdir': testdir_session['path']}
    yield session_project
    if os.path.exists(testdir_session['path']):
        os.chdir(os.path.join(testdir_session['path'], 'projects'))
        shutil.rmtree(session_project['name'], ignore_errors=True)


@pytest.mark.usefixtures("testdir_session")
@pytest.fixture(scope="class")
def project_class(testdir_session):
    project_name = Test_utils.random_string(4, 'project_')
    _create_project(testdir_session['path'], project_name)
    yield {
            'name': project_name,
            'testdir_fixture': testdir_session,
            'testdir': testdir_session['path']}
    os.chdir(os.path.join(testdir_session['path'], 'projects'))
    shutil.rmtree(project_name, ignore_errors=True)


@pytest.mark.usefixtures("testdir_session")
@pytest.fixture(scope="function")
def project_function(testdir_session):
    project_name = Test_utils.random_string(4, 'project_')
    _create_project(testdir_session['path'], project_name)
    yield {
            'name': project_name,
            'testdir_fixture': testdir_session,
            'testdir': testdir_session['path']}
    os.chdir(os.path.join(testdir_session['path'], 'projects'))
    shutil.rmtree(project_name, ignore_errors=True)


@pytest.mark.usefixtures("testdir_function")
@pytest.fixture(scope="function")
def project_function_clean(testdir_function):
    project_name = Test_utils.random_string(4, 'project_')
    _create_project(testdir_function['path'], project_name)
    yield {
            'name': project_name,
            'testdir_fixture': testdir_function,
            'testdir': testdir_function['path']}
    os.chdir(os.path.join(testdir_function['path'], 'projects'))
    shutil.rmtree(project_name, ignore_errors=True)


@pytest.fixture(scope="function")
def test_utils():    
    yield Test_utils


# TEST UTILS   

class Test_utils:

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
        return ''.join(random.choice(string.digits) for _ in range(length))

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
            f.write('{{"{0}": "{1}"\}}'.format(setting, setting_value))