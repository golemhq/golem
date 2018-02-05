import os
import shutil
import random
import string
import sys
from subprocess import call

import pytest

from . import helper_functions


BASE_DIR = None


def _get_base_dir():
    global BASE_DIR
    if not BASE_DIR:
        BASE_DIR = os.getcwd()
    return BASE_DIR


@pytest.fixture(scope="session")
def testdir_fixture():    
    base_dir = _get_base_dir()
    os.chdir(base_dir)
    test_dir_name = 'temp_directory_one'
    full_path = os.path.join(base_dir, test_dir_name)
    call(['golem-admin', 'createdirectory', test_dir_name])
    sys.path.append(full_path)
    yield {
            'path': full_path,
            'base_path': base_dir,
            'name': test_dir_name}
    os.chdir(base_dir)
    shutil.rmtree(test_dir_name, ignore_errors=True)


@pytest.fixture(scope="class")
def random_testdir_fixture():    
    base_dir = _get_base_dir()
    os.chdir(base_dir)
    test_dir_name = helper_functions.random_string(4, 'tesdir_')
    full_path = os.path.join(base_dir, test_dir_name)
    call(['golem-admin', 'createdirectory', test_dir_name])
    sys.path.append(full_path)
    yield {
            'path': full_path,
            'base_path': base_dir,
            'name': test_dir_name}
    os.chdir(base_dir)
    shutil.rmtree(test_dir_name, ignore_errors=True)


@pytest.mark.usefixtures("testdir_fixture")
@pytest.fixture(scope="class")
def project_fixture(testdir_fixture):
    project_name = 'temp_project_one'
    os.chdir(testdir_fixture['path'])
    call(['golem', 'createproject', project_name])
    _ = os.path.join(testdir_fixture['path'], 'projects', project_name)
    #sys.path.append(_)
    yield {
            'name': project_name,
            'testdir_fixture': testdir_fixture,
            'testdir': testdir_fixture['path']}
    os.chdir(os.path.join(testdir_fixture['path'], 'projects'))
    shutil.rmtree(project_name, ignore_errors=True)


@pytest.mark.usefixtures("random_testdir_fixture")
@pytest.fixture(scope="class")
def random_project_fixture(random_testdir_fixture):
    random_name = helper_functions.random_string(4, 'project_')
    os.chdir(random_testdir_fixture['path'])
    call(['golem', 'createproject', random_name])
    _ = os.path.join(random_testdir_fixture['path'], 'projects', random_name)
    #sys.path.append(_)
    # add project_path
    yield {
            'name': random_name,
            'testdir_fixture': random_testdir_fixture,
            'testdir': random_testdir_fixture['path']
            }
    os.chdir(os.path.join(random_testdir_fixture['path'], 'projects'))
    shutil.rmtree(random_name, ignore_errors=True)


#@pytest.mark.usefixtures("testdir_fixture")
@pytest.fixture(scope="session")
def permanent_project_fixture(testdir_fixture):
    random_name = helper_functions.random_string(4, 'project_')
    os.chdir(testdir_fixture['path'])
    call(['golem', 'createproject', random_name])
    _ = os.path.join(testdir_fixture['path'], 'projects', random_name)
    #sys.path.append(_)
    # add project_path
    yield {
            'name': random_name,
            'testdir_fixture': testdir_fixture,
            'testdir': testdir_fixture['path']}
    # os.chdir(os.path.join(testdir_fixture['path'], 'projects'))
    # shutil.rmtree(random_name, ignore_errors=True)