import os
import shutil
import random
import string
import sys
from subprocess import call

import pytest

BASE_DIR = None

# this is deprecated, sould be @pytest.fixture
# but travis uses an old version of pytest for python 3.4
# @pytest.yield_fixture(scope="session")
@pytest.fixture(scope="session")
def testdir_fixture():    
    global BASE_DIR
    if not BASE_DIR:
        BASE_DIR = os.getcwd()
    os.chdir(BASE_DIR)
    test_dir_name = 'temp_directory1'
    full_path = os.path.join(BASE_DIR, test_dir_name)
    call(['golem-admin', 'createdirectory', test_dir_name])
    sys.path.append(full_path)
    yield {
            'path': full_path,
            'base_path': BASE_DIR,
            'name': test_dir_name}
    os.chdir(BASE_DIR)
    shutil.rmtree(test_dir_name, ignore_errors=True)


@pytest.mark.usefixtures("testdir_fixture")
@pytest.fixture(scope="class")
def project_fixture(testdir_fixture):
    project_name = 'temp_project1'
    os.chdir(testdir_fixture['path'])
    call(['python', 'golem.py', 'createproject', project_name])
    sys.path.append(os.path.join(testdir_fixture['path'], project_name))
    yield {
            'testdir_fixture': testdir_fixture,
            'name': project_name}
    os.chdir(os.path.join(testdir_fixture['path'], 'projects'))
    shutil.rmtree(project_name)


@pytest.mark.usefixtures("testdir_fixture")
@pytest.fixture(scope="class")
def random_project_fixture(testdir_fixture):
    random_value = ''.join(random.choice(string.ascii_lowercase) for _ in range(4))
    random_name = 'project_' + random_value
    os.chdir(testdir_fixture['path'])
    call(['python', 'golem.py', 'createproject', random_name])
    yield {
            'testdir_fixture': testdir_fixture,
            'name': random_name}
    os.chdir(os.path.join(testdir_fixture['path'], 'projects'))
    shutil.rmtree(random_name)
