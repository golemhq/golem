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
        cmd = 'golem-admin createdirectory {}'.format(name)
        result = test_utils.run_command(cmd)
        full_path = os.path.join(dir_function.path, name)
        assert os.path.exists(full_path)
        expected = ('New golem test directory created at {}\n'
                    'Use credentials to access the GUI module:\n'
                    'user: admin\n'
                    'password: admin'.format(full_path))
        assert result == expected

    @pytest.mark.slow
    def test_createdirectory_absolute_path(self, dir_function, test_utils):
        """A test directory can be created using an absolute path"""
        name = 'testdir_test_003'
        full_path = os.path.join(dir_function.path, name)
        cmd = 'golem-admin createdirectory {}'.format(full_path)
        result = test_utils.run_command(cmd)
        assert os.path.exists(full_path)
        expected = ('New golem test directory created at {}\n'
                    'Use credentials to access the GUI module:\n'
                    'user: admin\n'
                    'password: admin'.format(full_path))
        assert result == expected

    @pytest.mark.slow
    def test_createdirectory_relative_path(self, dir_function, test_utils):
        """A test directory can be created using a relative path"""
        name = 'testdir_test_004'
        relative_path = os.path.join('dir2', name)
        cmd = 'golem-admin createdirectory {}'.format(relative_path)
        result = test_utils.run_command(cmd)
        full_path = os.path.join(dir_function.path, relative_path)
        assert os.path.exists(full_path)
        expected = ('New golem test directory created at {}\n'
                    'Use credentials to access the GUI module:\n'
                    'user: admin\n'
                    'password: admin'.format(full_path))
        assert result == expected

    @pytest.mark.slow
    def test_createdirectory_dot(self, dir_function, test_utils):
        """A test directory can be created in the current location"""
        cmd = 'golem-admin createdirectory .'
        result = test_utils.run_command(cmd)
        assert os.path.exists(dir_function.path)
        expected = ('New golem test directory created at {}\n'
                    'Use credentials to access the GUI module:\n'
                    'user: admin\n'
                    'password: admin'.format(dir_function.path))
        assert result == expected

    @pytest.mark.slow
    def test_createdirectory_not_empty(self, dir_function, test_utils):
        """A test directory can be created if the destination is not empty
        by confirming the operation
        """
        name = 'testdir_test_005'
        full_path = os.path.join(dir_function.path, name)
        os.mkdir(full_path)
        open(os.path.join(full_path, 'text-file.txt'), 'w').close()
        cmd = 'golem-admin createdirectory {} -y'.format(name)
        result = test_utils.run_command(cmd)
        expected = ('New golem test directory created at {}\n'
                    'Use credentials to access the GUI module:\n'
                    'user: admin\n'
                    'password: admin'.format(full_path))
        assert result == expected

    @pytest.mark.slow
    def test_createdirectory_existing_testdirectory(self, dir_function, test_utils):
        """A test directory can be created if the destination is not empty
        by confirming the operation
        """
        os.chdir(dir_function.path)
        name = 'testdir_test_006'
        full_path = os.path.join(dir_function.path, name)
        test_directory.create_test_directory(full_path)
        cmd = 'golem-admin createdirectory {} -y'.format(full_path)
        result = test_utils.run_command(cmd)
        expected = 'Error: target directory is already an existing Golem test directory'
        assert result == expected
