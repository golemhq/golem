import os

import pytest

from golem.cli import commands, messages
from golem.core import file_manager
from golem.gui.user_management import Users


class TestRunCommand:

    @pytest.mark.slow
    def test_golem_run_project_param_is_missing(self, project_session, capsys):
        project_session.activate()
        commands.run_command()
        captured = capsys.readouterr()
        assert messages.RUN_USAGE_MSG in captured.out

    @pytest.mark.slow
    def test_golem_run_project_does_not_exist(self, project_session):
        project_session.activate()
        with pytest.raises(SystemExit) as excinfo:
            commands.run_command(project='incorrect')
        assert str(excinfo.value) == 'golem run: error: the project incorrect does not exist'

    @pytest.mark.slow
    def test_golem_run_missing_test_query(self, project_session, capsys):
        _, project = project_session.activate()
        commands.run_command(project=project)
        captured = capsys.readouterr()
        assert messages.RUN_USAGE_MSG in captured.out

    @pytest.mark.slow
    def test_golem_run_suite(self, project_session, test_utils, caplog):
        _, project = project_session.activate()
        test_name = test_utils.create_random_test(project)
        suite_name = test_utils.random_string()
        test_utils.create_suite(project, suite_name, tests=[test_name])
        commands.run_command(project=project, test_query=suite_name)
        records = caplog.records
        assert records[0].message == 'Test execution started: {}'.format(test_name)
        assert records[2].message == 'Test Result: SUCCESS'
        # the execution report is created for suite
        path = os.path.join(project_session.path, 'reports', suite_name)
        assert os.path.isdir(path)
        timestamp = os.listdir(path)[0]
        report = os.path.join(path, timestamp, 'report.json')
        assert os.path.isfile(report)

    @pytest.mark.slow
    def test_golem_run_suite_in_folder(self, project_session, test_utils, caplog, capsys):
        testdir, project = project_session.activate()
        test_name = test_utils.create_random_test(project)
        suite_name = '{}.{}'.format(test_utils.random_string(), test_utils.random_string())
        test_utils.create_suite(project, suite_name, tests=[test_name])
        commands.run_command(project=project, test_query=suite_name)
        records = caplog.records
        assert records[0].message == 'Test execution started: {}'.format(test_name)
        assert records[2].message == 'Test Result: SUCCESS'
        out, err = capsys.readouterr()
        assert 'Tests found: 1' in out

    @pytest.mark.slow
    def test_golem_run_suite_py(self, project_session, test_utils, caplog):
        _, project = project_session.activate()
        test_name = test_utils.create_random_test(project)
        suite_name = test_utils.random_string()
        test_utils.create_suite(project, suite_name, tests=[test_name])
        with_extension = suite_name + '.py'
        commands.run_command(project=project, test_query=with_extension)
        records = caplog.records
        assert records[0].message == 'Test execution started: {}'.format(test_name)
        assert records[2].message == 'Test Result: SUCCESS'

    @pytest.mark.slow
    def test_golem_run_suite_py_in_folder(self, project_session, test_utils, caplog):
        _, project = project_session.activate()
        test_name = test_utils.create_random_test(project)
        random_dir = test_utils.random_string()
        suite_name = '{}.{}'.format(random_dir, 'suite_one')
        suite_query = os.path.join(random_dir, 'suite_one.py')
        test_utils.create_suite(project, suite_name, tests=[test_name])
        commands.run_command(project=project, test_query=suite_query)
        records = caplog.records
        assert records[0].message == 'Test execution started: {}'.format(test_name)
        assert records[2].message == 'Test Result: SUCCESS'

    @pytest.mark.slow
    def test_golem_run_test(self, project_session, test_utils, caplog):
        _, project = project_session.activate()
        test_name = test_utils.create_random_test(project)
        commands.run_command(project=project, test_query=test_name)
        records = caplog.records
        assert records[0].message == 'Test execution started: {}'.format(test_name)
        assert records[2].message == 'Test Result: SUCCESS'
        # the execution report is created for suite
        path = os.path.join(project_session.path, 'reports', 'single_tests', test_name)
        assert os.path.isdir(path)
        # only one timestamp
        assert len(os.listdir(path)) == 1

    @pytest.mark.slow
    def test_golem_run_test_py(self, project_session, test_utils, caplog):
        _, project = project_session.activate()
        test_name = test_utils.create_random_test(project)
        test_query = '{}.py'.format(test_name)
        commands.run_command(project=project, test_query=test_query)
        records = caplog.records
        assert records[0].message == 'Test execution started: {}'.format(test_name)
        assert records[2].message == 'Test Result: SUCCESS'
        # the execution report is created for suite
        path = os.path.join(project_session.path, 'reports', 'single_tests', test_name)
        assert os.path.isdir(path)
        # only one timestamp
        assert len(os.listdir(path)) == 1

    @pytest.mark.slow
    def test_golem_run_test_in_folder(self, project_session, test_utils, caplog):
        _, project = project_session.activate()
        test_name = '{}.test_one'.format(test_utils.random_string())
        test_utils.create_test(project, test_name)
        commands.run_command(project=project, test_query=test_name)
        records = caplog.records
        assert records[0].message == 'Test execution started: {}'.format(test_name)
        assert records[4].message == 'Test Result: SUCCESS'

    @pytest.mark.slow
    def test_golem_run_test_py_in_folder(self, project_function, test_utils, caplog):
        _, project = project_function.activate()
        test_utils.create_test(project, 'folder.test_one')
        commands.run_command(project=project, test_query='folder/test_one.py')
        records = caplog.records
        assert records[0].message == 'Test execution started: folder.test_one'
        assert records[4].message == 'Test Result: SUCCESS'

    @pytest.mark.slow
    @pytest.mark.skipif("os.name != 'nt'")
    def test_golem_run_test_py_in_folder_windows_path(self, project_function, test_utils,
                                                      caplog):
        _, project = project_function.activate()
        test_utils.create_test(project, 'folder.test_one')
        commands.run_command(project=project, test_query='folder\\test_one.py')
        records = caplog.records
        assert records[0].message == 'Test execution started: folder.test_one'
        assert records[4].message == 'Test Result: SUCCESS'

    @pytest.mark.slow
    def test_golem_run_directory(self, project_function, test_utils):
        _, project = project_function.activate()
        test_utils.create_test(project, 'test_one')
        test_utils.create_test(project, 'foo.test_two')
        test_utils.create_test(project, 'foo.test_three')
        test_utils.create_test(project, 'foo.bar.test_four')
        commands.run_command(project=project, test_query='foo')
        reportsdir = os.path.join(project_function.path, 'reports', 'foo')
        assert os.path.isdir(reportsdir)
        assert len(os.listdir(reportsdir)) == 1
        timestamp = os.listdir(reportsdir)[0]
        timestampdir = os.path.join(reportsdir, timestamp)
        tests = os.listdir(timestampdir)
        assert len(tests) == 4
        assert 'foo.test_two' in tests
        assert 'foo.test_three' in tests
        assert 'foo.bar.test_four' in tests
        assert 'test_one' not in tests

    @pytest.mark.slow
    def test_golem_run_directory_all_tests(self, project_function, test_utils):
        _, project = project_function.activate()
        test_utils.create_test(project, 'test_one')
        test_utils.create_test(project, 'foo.test_two')
        test_utils.create_test(project, 'foo.bar.test_three')
        commands.run_command(project=project, test_query='.')
        reportsdir = os.path.join(project_function.path, 'reports', 'all')
        assert os.path.isdir(reportsdir)
        assert len(os.listdir(reportsdir)) == 1
        timestamp = os.listdir(reportsdir)[0]
        timestampdir = os.path.join(reportsdir, timestamp)
        tests = os.listdir(timestampdir)
        assert len(tests) == 4
        assert 'test_one' in tests
        assert 'foo.test_two' in tests
        assert 'foo.bar.test_three' in tests

    @pytest.mark.slow
    def test_golem_run_directory_no_tests_present(self, project_function, capsys):
        _, project = project_function.activate()
        # run all tests, there are no tests in project
        commands.run_command(project=project, test_query='.')
        msg = 'No tests were found in {}'.format(os.path.join('tests', ''))
        out, err = capsys.readouterr()
        assert msg in out
        # run tests in an empty directory
        path = os.path.join(project_function.path, 'tests', 'foo')
        file_manager.create_directory(path=path, add_init=True)
        commands.run_command(project=project, test_query='foo')
        msg = 'No tests were found in {}'.format(os.path.join('tests', 'foo'))
        out, err = capsys.readouterr()
        assert msg in out


class TestCreateDirectoryCommand:

    def test_createdirectory_command(self, dir_function):
        os.chdir(dir_function.path)
        name = 'testdirectory_002'
        commands.createdirectory_command(name)
        testdir = os.path.join(dir_function.path, name)
        assert os.path.isdir(testdir)


class TestCreateSuperUserCommand:

    def test_create_superuser_command(self, testdir_class, test_utils, capsys):
        testdir_class.activate()
        username = test_utils.random_string(5)
        email = test_utils.random_email()
        password = test_utils.random_string(5)
        commands.createsuperuser_command(username, email, password, no_input=True)
        out, err = capsys.readouterr()
        msg = 'Superuser {} was created successfully.'.format(username)
        assert msg in out
        assert Users.user_exists(username)
        user = Users.get_user_by_username(username)
        assert user.email == email

    def test_create_superuser_command_invalid_email(self, testdir_class, test_utils, capsys):
        testdir_class.activate()
        username = test_utils.random_string(5)
        email = 'test@'
        password = test_utils.random_string(5)
        with pytest.raises(SystemExit) as wrapped_execution:
            commands.createsuperuser_command(username, email, password, no_input=True)
        assert wrapped_execution.value.code == 1
        captured = capsys.readouterr()
        assert 'Error: {} is not a valid email address'.format(email) in captured.out

    def test_create_superuser_command_no_email(self, testdir_class, test_utils):
        testdir_class.activate()
        username = test_utils.random_string(5)
        password = test_utils.random_string(5)
        commands.createsuperuser_command(username, None, password, no_input=True)
        user = Users.get_user_by_username(username)
        assert user.email is None


class TestExitStatuses:
    content = """
description = 'A test which deliberately fails'

def setup(data):
    pass

def test(data):
    step('test step')
    raise Exception('Intentional exception to trigger exit status == 1')

def teardown(data):
    pass
"""

    @pytest.mark.slow
    def test_exit_code_one_on_test_failure_when_using_single_processing_capabilities(
            self, project_function, test_utils):
        _, project = project_function.activate()
        test_utils.create_test(project, 'test_one', content=self.content)
        test_utils.create_test(project, 'test_two')

        with pytest.raises(SystemExit) as wrapped_execution:
            commands.run_command(project=project, test_query='.', processes=1)

        assert wrapped_execution.value.code == 1

    @pytest.mark.slow
    def test_exit_code_one_on_test_failure_when_using_multi_processing_capabilities(
            self, project_function, test_utils):
        _, project = project_function.activate()
        test_utils.create_test(project, 'test_one', content=self.content)
        test_utils.create_test(project, 'test_two')

        with pytest.raises(SystemExit) as wrapped_execution:
            commands.run_command(project=project, test_query='.', processes=2)

        assert wrapped_execution.value.code == 1
