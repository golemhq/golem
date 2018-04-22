import os
import shutil
from subprocess import call

import pytest

from . import helper_functions


BASE_DIR = None

session_testdir = {}

session_project = {}


def get_base_dir():
    global BASE_DIR
    if not BASE_DIR:
        BASE_DIR = os.getcwd()
    return BASE_DIR


def _create_testdir(base_dir):
    os.chdir(base_dir)
    testdir_name = helper_functions.random_string(4, 'testdir_')
    full_path = os.path.join(base_dir, testdir_name)
    call(['golem-admin', 'createdirectory', testdir_name])
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


@pytest.mark.usefixtures("testdir_session")
@pytest.fixture(scope="session")
def project_session(testdir_session):
    global session_project
    if not session_project:
        project_name = helper_functions.random_string(4, 'project_')
        os.chdir(testdir_session['path'])
        call(['golem', 'createproject', project_name])
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
    project_name = helper_functions.random_string(4, 'project_')
    os.chdir(testdir_session['path'])
    call(['golem', 'createproject', project_name])
    yield {
            'name': project_name,
            'testdir_fixture': testdir_session,
            'testdir': testdir_session['path']}
    os.chdir(os.path.join(testdir_session['path'], 'projects'))
    shutil.rmtree(project_name, ignore_errors=True)

