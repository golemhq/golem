import os

from golem.cli import commands


class TestCreateDirectoryCommand:

    def test_createdirectory_command(self, dir_function):
        name = 'testdirectory_002'
        commands.createdirectory_command(name)
        testdir = os.path.join(dir_function.path, name)
        assert os.path.isdir(testdir)
