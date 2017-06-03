import os

from tests.fixtures import test_directory_fixture


class Test_startdirectory:

    def test_start_new_directory(self, test_directory_fixture):
        assert os.path.isdir(test_directory_fixture['full_path'])

    def test_new_directory_contents(self, test_directory_fixture):
        listdir = os.listdir(test_directory_fixture['full_path'])
        files = [name for name in listdir 
                 if os.path.isfile(os.path.join(test_directory_fixture['full_path'],
                                   name))]
        dirs = [name for name in listdir 
                 if os.path.isdir(os.path.join(test_directory_fixture['full_path'],
                                  name))]
        if '.DS_Store' in files:
            files.remove('.DS_Store')
        assert len(files) == 4
        # verify the correct files exist
        assert '__init__.py' in files
        assert 'golem.py' in files
        assert 'settings.json' in files
        assert 'users.json' in files
        # verify there are 2 directories
        assert len(dirs) == 2
        # verify the test dir contains the correct directories
        assert 'projects' in dirs
        assert 'drivers' in dirs
