import os
import shutil
from subprocess import call

import pytest


# this is deprecated, sould be @pytest.fixture
# but travis uses an old version of pytest for python 3.4
@pytest.yield_fixture(scope="class")
def test_directory_fixture():    
    base_dir = os.getcwd()
    test_dir_name = 'temp_directory1'
    full_path = os.path.join(base_dir, test_dir_name)
    if os.path.exists(full_path):
      shutil.rmtree(test_dir_name)
    call(['golem-admin', 'createdirectory', test_dir_name])
    yield {'full_path': full_path,
           'base_path': base_dir,
           'test_directory_name': test_dir_name}
    os.chdir(base_dir)
    shutil.rmtree(test_dir_name)


@pytest.mark.usefixtures("test_directory")
@pytest.yield_fixture(scope="class")
def project_fixture(test_directory_fixture):
	project_name = 'temp_project1'
	os.chdir(test_directory_fixture['test_directory_name'])
	call(['python', 'golem.py', 'createproject', project_name])
	yield {'test_directory_fixture': test_directory_fixture,
            'project_name': project_name}