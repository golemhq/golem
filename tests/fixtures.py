import os
import shutil
from subprocess import call

import pytest


@pytest.fixture(scope="module")
def test_directory():    
    base_dir = os.getcwd()
    test_dir_name = os.path.join(base_dir, 'temp_directory1')
    call(['golem-admin', 'startdirectory', test_dir_name], shell=True)
    yield (test_dir_name)
    os.chdir(base_dir)
    shutil.rmtree(test_dir_name)


@pytest.mark.usefixtures("test_directory")
@pytest.fixture(scope="module")
def project(test_directory):
	project_name = 'temp_project1'
	os.chdir(test_directory)
	call(['python', 'golem.py', 'startproject', project_name], shell=True)
	yield (test_directory, project_name)