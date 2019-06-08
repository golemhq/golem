import os

from golem.core import test_directory


class TestCreateTestDir:

    def test_new_directory_contents(self, dir_function, test_utils):
        name = test_utils.random_string(10)
        os.chdir(dir_function.path)
        testdir = os.path.join(dir_function.path, name)
        test_directory.create_test_directory(testdir)
        listdir = os.listdir(testdir)
        files = [name for name in listdir if os.path.isfile(os.path.join(testdir, name))]
        dirs = [name for name in listdir if os.path.isdir(os.path.join(testdir, name))]
        if '.DS_Store' in files:
            files.remove('.DS_Store')
        assert len(files) == 4
        # verify files
        assert '__init__.py' in files
        assert 'settings.json' in files
        assert 'users.json' in files
        assert '.golem' in files
        # verify directories
        assert len(dirs) == 2
        # verify the test dir contains the correct directories
        assert 'projects' in dirs
        assert 'drivers' in dirs
