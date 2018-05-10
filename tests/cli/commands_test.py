import os

from golem.cli import commands


class Test_createdirectory_command:

    def test_createdirectory_command(self, dir_function):
        path = dir_function['path']
        name = 'testdirectory_002'
        commands.createdirectory_command(name)
        testdir = os.path.join(path, name)
        assert os.path.isdir(testdir)
