import os

from tests.fixtures import testdir_fixture


class Test_startdirectory:

    def test_start_new_directory(self, testdir_fixture):
        assert os.path.isdir(testdir_fixture['path'])

    def test_new_directory_contents(self, testdir_fixture):
        listdir = os.listdir(testdir_fixture['path'])
        files = [name for name in listdir 
                 if os.path.isfile(os.path.join(testdir_fixture['path'], name))]
        dirs = [name for name in listdir 
                 if os.path.isdir(os.path.join(testdir_fixture['path'], name))]
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
