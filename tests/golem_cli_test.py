import os

import pytest

from golem.cli import messages
from golem.gui import user
from golem.core import utils

from .fixtures import testdir_session, project_session
from .helper_functions import run_command


class Test_golem:

    run_commands = [
        ('golem', messages.USAGE_MSG),
        ('golem -h', messages.USAGE_MSG),
        ('golem --help', messages.USAGE_MSG),
        ('golem -h run', messages.RUN_USAGE_MSG),
        ('golem -h gui', messages.GUI_USAGE_MSG),
        ('golem -h createproject', messages.CREATEPROJECT_USAGE_MSG),
        ('golem -h createtest', messages.CREATETEST_USAGE_MSG),
        ('golem -h createsuite', messages.CREATESUITE_USAGE_MSG),
        ('golem -h createuser', messages.CREATEUSER_USAGE_MSG),
        ('golem run -h', messages.RUN_USAGE_MSG),
        ('golem gui -h', messages.GUI_USAGE_MSG),
    ]

    @pytest.mark.parametrize('command,expected', run_commands)
    def test_golem_command_output(self, command, expected, testdir_session):
        path = testdir_session['path']
        os.chdir(path)
        result = run_command(command)
        assert result == expected

    def test_golem_createproject(self, testdir_session):
        path = testdir_session['path']
        os.chdir(path)
        project = 'testproject1'
        result = run_command('golem createproject {}'.format(project))
        assert result == 'Project {} created'.format(project)
        projects = utils.get_projects(path)
        assert project in projects

    def test_golem_createsuite(self, project_session):
        path = project_session['testdir']
        project = project_session['name']
        os.chdir(path)
        suite = 'suite1'
        command = ('golem createsuite {} {}'.format(project, suite))
        result = run_command(command)
        msg = 'Suite {} created for project {}'.format(suite, project)
        assert result == msg
        spath = os.path.join(path, 'projects', project, 'suites', suite+'.py')
        assert os.path.isfile(spath)

    def test_golem_createtest(self, project_session):
        path = project_session['testdir']
        project = project_session['name']
        os.chdir(path)
        test = 'test1'
        command = ('golem createtest {} {}'.format(project, test))
        result = run_command(command)
        msg = 'Test {} created for project {}'.format(test, project)
        assert result == msg
        tpath = os.path.join(path, 'projects', project, 'tests', test+'.py')
        assert os.path.isfile(tpath)

    def test_golem_createuser(self, testdir_session):
        path = testdir_session['path']
        os.chdir(path)
        username = 'user1'
        password = '123456'
        command = ('golem createuser {} {}'.format(username, password))
        result = run_command(command)
        msg = 'User {} was created successfully'.format(username)
        assert result == msg
        assert user.user_exists(username, path)

    def test_golem_run_test(self, project_session):
        path = project_session['testdir']
        project = project_session['name']
        os.chdir(path)
        test = 'test2'
        command = ('golem createtest {} {}'.format(project, test))
        run_command(command)
        command = ('golem run {} {}'.format(project, test))
        result = run_command(command)
        # TODO: the result is not in order
        assert 'Executing:' in result
        assert '{} in chrome with the following data: {{}}'.format(test) in result
        assert 'INFO Test execution started: {}'.format(test) in result
        assert 'INFO Browser: chrome' in result
        assert 'INFO Test passed' in result

    def test_golem_run_suite(self, project_session):
        path = project_session['testdir']
        project = project_session['name']
        os.chdir(path)
        suite = 'suite2'
        command = ('golem createsuite {} {}'.format(project, suite))
        run_command(command)
        command = ('golem run {} {}'.format(project, suite))
        result = run_command(command)
        # TODO: the result is not in order
        assert 'Executing:' in result
        assert 'Warning: no tests were found' in result


    def test_golem_createproject_no_args(self, testdir_session):
        path = testdir_session['path']
        os.chdir(path)
        result = run_command('golem createproject')
        expected = ('usage: golem createproject [-h] project\n'
                    'golem createproject: error: the following arguments are required: project')
        assert result == expected


    def test_golem_createproject_project_exists(self, project_session):
        path = project_session['testdir']
        project = project_session['name']
        os.chdir(path)
        result = run_command('golem createproject {}'.format(project))
        expected = ('golem.core.exceptions.CommandException: '
                    'a project with the name \'{}\' already exists'
                    .format(project))
        assert expected in result

    def test_golem_createsuite_no_args(self, project_session):
        path = project_session['testdir']
        project = project_session['name']
        os.chdir(path)
        result = run_command('golem createsuite')
        expected = ('usage: golem createsuite [-h] project suite\n'
                    'golem createsuite: error: the following arguments '
                    'are required: project, suite')
        assert result == expected

    def test_golem_createsuite_project_does_not_exist(self, testdir_session):
        path = testdir_session['path']
        os.chdir(path)
        project = 'project_does_not_exist'
        suite = 'suite_test_00002'
        result = run_command('golem createsuite {} {}'.format(project, suite))
        expected = ('golem.core.exceptions.CommandException: '
                    'Error: a project with that name does not exist')
        assert expected in result

    def test_golem_createsuite_already_exists(self, project_session):
        path = project_session['testdir']
        project = project_session['name']
        os.chdir(path)
        suite = 'suite_test_00003'
        command = 'golem createsuite {} {}'.format(project, suite)
        run_command(command)
        result = run_command(command)
        expected = ('golem.core.exceptions.CommandException: A suite '
                    'with that name already exists')
        assert expected in result

    def test_golem_createtest_no_args(self, project_session):
        path = project_session['testdir']
        project = project_session['name']
        os.chdir(path)
        result = run_command('golem createtest')
        expected = ('usage: golem createtest [-h] project test\n'
                    'golem createtest: error: the following arguments '
                    'are required: project, test')
        assert result == expected

    def test_golem_createtest_project_not_exist(self, testdir_session):
        path = testdir_session['path']
        os.chdir(path)
        project = 'project_not_exist'
        test = 'test_0004'
        result = run_command('golem createtest {} {}'.format(project, test))
        expected = ('golem.core.exceptions.CommandException: Error: a '
                    'project with that name does not exist')
        assert expected in result

    def test_golem_createtest_already_exists(self, project_session):
        path = project_session['testdir']
        project = project_session['name']
        os.chdir(path)
        test = 'test_0005'
        run_command('golem createtest {} {}'.format(project, test))
        result = run_command('golem createtest {} {}'.format(project, test))
        expected = ('golem.core.exceptions.CommandException: A test '
                    'with that name already exists')
        assert expected in result

    def test_golem_run_no_args(self, project_session):
        path = project_session['testdir']
        project = project_session['name']
        os.chdir(path)
        result = run_command('golem run')
        expected = messages.RUN_USAGE_MSG
        expected += '\nProjects:'
        for proj in utils.get_projects(path):
            expected += '\n  {}'.format(proj)
        assert result == expected

    def test_golem_run_test_b_flag(self, project_session):
        path = project_session['testdir']
        project = project_session['name']
        os.chdir(path)
        test = 'test2'
        command = ('golem createtest {} {}'.format(project, test))
        run_command(command)
        command = ('golem run {} {} -b firefox'.format(project, test))
        result = run_command(command)
        # TODO: the result is not in order
        assert 'Executing:' in result
        assert '{} in firefox with the following data: {{}}'.format(test) in result
        assert 'INFO Test execution started: {}'.format(test) in result
        assert 'INFO Browser: firefox' in result
        assert 'INFO Test passed' in result