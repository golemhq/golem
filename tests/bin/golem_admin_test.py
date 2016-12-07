import os

from tests.fixtures import test_directory


class Test_startdirectory:

    def test_start_new_directory(self, test_directory):
        assert os.path.isdir(test_directory)

    def test_new_directory_contents(self, test_directory):
        # verify there are 4 files inside the new test directory
        listdir = os.listdir(test_directory)
        files = [name for name in listdir 
                 if os.path.isfile(os.path.join(test_directory, name))]
        dirs = [name for name in listdir 
                 if os.path.isdir(os.path.join(test_directory, name))]
        assert len(files) == 4
        # verify the correct files exist
        assert '__init__.py' in files
        assert 'golem.py' in files
        assert 'settings.conf' in files
        assert 'users.json' in files
        # verify there is only one directory
        assert len(dirs) == 1
        # verify the name of the directory is correct
        assert 'projects' in dirs
