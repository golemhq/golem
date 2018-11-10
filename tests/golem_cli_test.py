import os

import pytest

from golem.cli import messages
from golem.gui import user
from golem.core import utils


class TestGolem:

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
    def test_golem_command_output(self, command, expected, testdir_session, test_utils):
        os.chdir(testdir_session.path)
        result = test_utils.run_command(command)
        assert result == expected

    def test_golem_createproject(self, testdir_session, test_utils):
        os.chdir(testdir_session.path)
        project = 'testproject1'
        cmd = 'golem createproject {}'.format(project)
        result = test_utils.run_command(cmd)
        assert result == 'Project {} created'.format(project)
        projects = utils.get_projects(testdir_session.path)
        assert project in projects

    def test_golem_createsuite(self, project_session, test_utils):
        path = project_session.testdir
        project = project_session.name
        os.chdir(path)
        suite = 'suite1'
        command = 'golem createsuite {} {}'.format(project, suite)
        result = test_utils.run_command(command)
        msg = 'Suite {} created for project {}'.format(suite, project)
        assert result == msg
        spath = os.path.join(path, 'projects', project, 'suites', suite+'.py')
        assert os.path.isfile(spath)

    def test_golem_createtest(self, project_session, test_utils):
        path = project_session.testdir
        project = project_session.name
        os.chdir(path)
        test = 'test1'
        command = 'golem createtest {} {}'.format(project, test)
        result = test_utils.run_command(command)
        msg = 'Test {} created for project {}'.format(test, project)
        assert result == msg
        tpath = os.path.join(path, 'projects', project, 'tests', test+'.py')
        assert os.path.isfile(tpath)

    def test_golem_createuser(self, testdir_session, test_utils):
        os.chdir(testdir_session.path)
        username = 'user1'
        password = '123456'
        command = 'golem createuser {} {}'.format(username, password)
        result = test_utils.run_command(command)
        msg = 'User {} was created successfully'.format(username)
        assert result == msg
        assert user.user_exists(username, testdir_session.path)

    def test_golem_run_test(self, project_session, test_utils):
        path = project_session.testdir
        project = project_session.name
        os.chdir(path)
        test = 'test2'
        command = 'golem createtest {} {}'.format(project, test)
        test_utils.run_command(command)
        command = 'golem run {} {}'.format(project, test)
        result = test_utils.run_command(command)
        assert 'INFO Test execution started: {}'.format(test) in result
        assert 'INFO Browser: chrome' in result
        assert 'INFO Test Result: SUCCESS' in result

    def test_golem_run_suite(self, project_session, test_utils):
        path = project_session.testdir
        project = project_session.name
        os.chdir(path)
        suite = 'suite2'
        command = 'golem createsuite {} {}'.format(project, suite)
        test_utils.run_command(command)
        command = 'golem run {} {}'.format(project, suite)
        result = test_utils.run_command(command)
        assert 'No tests were found' in result

    def test_golem_createproject_no_args(self, testdir_session, test_utils):
        os.chdir(testdir_session.path)
        result = test_utils.run_command('golem createproject')
        expected = ('usage: golem createproject [-h] project\n'
                    'golem createproject: error: the following '
                    'arguments are required: project')
        assert result == expected

    def test_golem_createproject_project_exists(self, project_session, test_utils):
        path = project_session.testdir
        project = project_session.name
        os.chdir(path)
        cmd = 'golem createproject {}'.format(project)
        result = test_utils.run_command(cmd)
        expected = ('golem createproject: error: a project with name \'{}\' already exists'
                    .format(project))
        assert result == expected

    def test_golem_createsuite_no_args(self, project_session, test_utils):
        path = project_session.testdir
        os.chdir(path)
        result = test_utils.run_command('golem createsuite')
        expected = ('usage: golem createsuite [-h] project suite\n'
                    'golem createsuite: error: the following arguments '
                    'are required: project, suite')
        assert result == expected

    def test_golem_createsuite_project_does_not_exist(self, testdir_session, test_utils):
        os.chdir(testdir_session.path)
        project = 'project_does_not_exist'
        suite = 'suite_test_00002'
        cmd = 'golem createsuite {} {}'.format(project, suite)
        result = test_utils.run_command(cmd)
        expected = ('golem createsuite: error: a project with name {} '
                    'does not exist'.format(project))
        assert result == expected

    def test_golem_createsuite_already_exists(self, project_session, test_utils):
        path = project_session.testdir
        project = project_session.name
        os.chdir(path)
        suite = 'suite_test_00003'
        command = 'golem createsuite {} {}'.format(project, suite)
        test_utils.run_command(command)
        result = test_utils.run_command(command)
        expected = ('golem createsuite: error: a suite '
                    'with that name already exists')
        assert result == expected

    def test_golem_createtest_no_args(self, project_session, test_utils):
        path = project_session.testdir
        os.chdir(path)
        result = test_utils.run_command('golem createtest')
        expected = ('usage: golem createtest [-h] project test\n'
                    'golem createtest: error: the following arguments '
                    'are required: project, test')
        assert result == expected

    def test_golem_createtest_project_not_exist(self, testdir_session, test_utils):
        os.chdir(testdir_session.path)
        project = 'project_not_exist'
        test = 'test_0004'
        cmd = 'golem createtest {} {}'.format(project, test)
        result = test_utils.run_command(cmd)
        expected = ('golem createtest: error: a project with name {} '
                    'does not exist'.format(project))
        assert result == expected

    def test_golem_createtest_already_exists(self, project_session, test_utils):
        path = project_session.testdir
        project = project_session.name
        os.chdir(path)
        test = 'test_0005'
        cmd = 'golem createtest {} {}'.format(project, test)
        test_utils.run_command(cmd)
        result = test_utils.run_command(cmd)
        expected = ('golem createtest: error: a test with that name already exists')
        assert result == expected

    def test_golem_run_no_args(self, project_session, test_utils):
        path = project_session.testdir
        os.chdir(path)
        result = test_utils.run_command('golem run')
        expected = messages.RUN_USAGE_MSG
        expected += '\nProjects:'
        for proj in utils.get_projects(path):
            expected += '\n  {}'.format(proj)
        assert result == expected

    def test_golem_run_test_b_flag(self, project_session, test_utils):
        path = project_session.testdir
        project = project_session.name
        os.chdir(path)
        test = 'test2'
        command = 'golem createtest {} {}'.format(project, test)
        test_utils.run_command(command)
        command = 'golem run {} {} -b firefox'.format(project, test)
        result = test_utils.run_command(command)
        assert 'INFO Test execution started: {}'.format(test) in result
        assert 'INFO Browser: firefox' in result
        assert 'INFO Test Result: SUCCESS' in result

    def test_golem_run_not_match_test_or_suite(self, project_session, test_utils):
        path = project_session.testdir
        project = project_session.name
        os.chdir(path)
        test = 'test001_does_not_exist'
        command = 'golem run {} {}'.format(project, test)
        result = test_utils.run_command(command)
        expected = ('golem run: error: the value {0} does not match '
                    'an existing test or suite'.format(test))
        assert result == expected

    def test_golem_run_project_does_not_exist(self, testdir_session, test_utils):
        project = 'project_does_not_exist_4564546'
        os.chdir(testdir_session.path)
        test = 'test002_does_not_exist'
        command = 'golem run {} {}'.format(project, test)
        result = test_utils.run_command(command)
        expected = ('golem run: error: the project {0} does not exist'.format(project))
        assert result == expected
