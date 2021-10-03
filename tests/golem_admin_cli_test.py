import os

import pytest

from golem.core import test_directory
from golem.cli import messages


class TestGolemAdmin:

    run_commands = [
        ('golem-admin', messages.ADMIN_USAGE_MSG),
        ('golem-admin -h', messages.ADMIN_USAGE_MSG),
        ('golem-admin --help', messages.ADMIN_USAGE_MSG),
        ('golem-admin -h createdirectory', messages.ADMIN_USAGE_MSG)
    ]

    @pytest.mark.slow
    @pytest.mark.parametrize('command,expected', run_commands,)
    def test_golem_admin_command_output(self, command, expected, test_utils):
        result = test_utils.run_command(command)
        assert result == expected

    @pytest.mark.slow
    def test_createdirectory_whitout_args(self, test_utils):
        result = test_utils.run_command('golem-admin createdirectory')
        expected = ('usage: golem-admin createdirectory [-y] [-h] name\n'
                    'golem-admin createdirectory: error: the following '
                    'arguments are required: name')
        assert result == expected

    @pytest.mark.slow
    def test_createdirectory(self, dir_function, test_utils):
        name = 'testdir_test_002'
        cmd = f'golem-admin createdirectory {name}'
        result = test_utils.run_command(cmd)
        full_path = os.path.join(dir_function.path, name)
        assert os.path.exists(full_path)
        expected = (f'New golem test directory created at {full_path}\n'
                    'Use these credentials to access the GUI module:\n'
                    '  user:     admin\n'
                    '  password: admin\n'
                    'Would you like to download ChromeDriver now? [Y/n]')
        assert expected in result

    @pytest.mark.slow
    def test_createdirectory_existing_testdirectory(self, dir_function, test_utils):
        """A test directory can be created if the destination is not empty
        by confirming the operation
        """
        os.chdir(dir_function.path)
        name = 'testdir_test_006'
        full_path = os.path.join(dir_function.path, name)
        test_directory.create_test_directory(full_path)
        cmd = f'golem-admin createdirectory {full_path} -y'
        result = test_utils.run_command(cmd)
        expected = 'Error: target directory is already an existing Golem test directory'
        assert result == expected
