import os

import pytest

from golem.cli import messages
from golem.gui import user
from golem.core import utils


class Test_golem_admin:

    run_commands = [
        ('golem-admin', messages.ADMIN_USAGE_MSG),
        ('golem-admin -h', messages.ADMIN_USAGE_MSG),
        ('golem-admin --help', messages.ADMIN_USAGE_MSG),
        ('golem-admin -h createdirectory', messages.ADMIN_USAGE_MSG)
    ]

    @pytest.mark.parametrize('command,expected', run_commands,)
    def test_golem_admin_command_output(self, command, expected, test_utils):
        result = test_utils.run_command(command)
        assert result == expected

    def test_createdirectory_whitout_args(self, test_utils):
        result = test_utils.run_command('golem-admin createdirectory')
        expected = ('usage: golem-admin createdirectory [-h] name\n'
                    'golem-admin createdirectory: error: the following '
                    'arguments are required: name')
        assert result == expected
    
    def test_createdirectory_already_exists(self, dir_function, test_utils):
        path = dir_function['path']
        name = 'testdir_001'
        os.chdir(path)
        os.mkdir(name)
        cmd = 'golem-admin createdirectory {}'.format(name)
        result = test_utils.run_command(cmd)
        expected = ('golem-admin createdirectory: error: the directory {} '
                    'already exists'.format(name))
        assert result == expected

    def test_createdirectory(self, dir_function, test_utils):
        path = dir_function['path']
        name = 'testdir_test_002'
        os.chdir(path)
        cmd = 'golem-admin createdirectory {}'.format(name)
        result = test_utils.run_command(cmd)
        full_path = os.path.join(path, name)
        expected = ('New golem test directory created at {}\n'
                    'Use credentials to access the GUI module:\n'
                    'user: admin\n'
                    'password: admin'.format(full_path))
        assert result == expected
