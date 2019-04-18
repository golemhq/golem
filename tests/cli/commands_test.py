import os

import pytest

from golem.cli import commands, messages
from golem.core import file_manager


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
    def test_golem_run_suite(self, project_function, test_utils, caplog):
        testdir, project = project_function.activate()
        test_name = 'test_one'
        test_utils.create_test(project, [], test_name)
        test_utils.create_suite(project, 'suite_one', tests=[test_name])
        commands.run_command(project=project, test_query='suite_one')
        records = caplog.records
        assert records[0].message == 'Test execution started: {}'.format(test_name)
        assert records[4].message == 'Test Result: SUCCESS'
        # the execution report is created for suite
        path = os.path.join(project_function.path, 'reports', 'suite_one')
        assert os.path.isdir(path)
        timestamp = os.listdir(path)[0]
        report = os.path.join(path, timestamp, 'report.json')
        assert os.path.isfile(report)

    @pytest.mark.slow
    def test_golem_run_suite_in_folder(self, project_function, test_utils, caplog, capsys):
        testdir, project = project_function.activate()
        test_name = 'test_one'
        test_utils.create_test(project, [], test_name)
        test_utils.create_suite(project, 'folder.suite_one', tests=[test_name])
        commands.run_command(project=project, test_query='folder.suite_one')
        records = caplog.records
        assert records[0].message == 'Test execution started: {}'.format(test_name)
        assert records[4].message == 'Test Result: SUCCESS'
        out, err = capsys.readouterr()
        assert 'Tests found: 1' in out

    @pytest.mark.slow
    def test_golem_run_suite_py(self, project_function, test_utils, caplog):
        _, project = project_function.activate()
        test_name = 'test_one'
        test_utils.create_test(project, [], test_name)
        test_utils.create_suite(project, 'suite_one', tests=[test_name])
        commands.run_command(project=project, test_query='suite_one.py')
        records = caplog.records
        assert records[0].message == 'Test execution started: {}'.format(test_name)
        assert records[4].message == 'Test Result: SUCCESS'

    @pytest.mark.slow
    def test_golem_run_suite_py_in_folder(self, project_function, test_utils, caplog):
        _, project = project_function.activate()
        test_name = 'test_one'
        test_utils.create_test(project, [], test_name)
        test_utils.create_suite(project, 'folder.suite_one', tests=[test_name])
        commands.run_command(project=project, test_query='folder/suite_one.py')
        records = caplog.records
        assert records[0].message == 'Test execution started: {}'.format(test_name)
        assert records[4].message == 'Test Result: SUCCESS'

    @pytest.mark.slow
    @pytest.mark.skipif("os.name != 'nt'")
    def test_golem_run_suite_py_in_folder_windows_path(self, project_function, test_utils,
                                                       caplog):
        _, project = project_function.activate()
        test_name = 'test_one'
        test_utils.create_test(project, [], test_name)
        test_utils.create_suite(project, 'folder.suite_one', tests=[test_name])
        commands.run_command(project=project, test_query='folder\\suite_one.py')
        records = caplog.records
        assert records[0].message == 'Test execution started: {}'.format(test_name)
        assert records[4].message == 'Test Result: SUCCESS'

    @pytest.mark.slow
    def test_golem_run_test(self, project_function, test_utils, caplog):
        _, project = project_function.activate()
        test_name = 'test_one'
        test_utils.create_test(project, [], test_name)
        commands.run_command(project=project, test_query='test_one')
        records = caplog.records
        assert records[0].message == 'Test execution started: {}'.format(test_name)
        assert records[4].message == 'Test Result: SUCCESS'
        # the execution report is created for suite
        path = os.path.join(project_function.path, 'reports', 'single_tests', 'test_one')
        assert os.path.isdir(path)
        # only one timestamp
        assert len(os.listdir(path)) == 1

    @pytest.mark.slow
    def test_golem_run_test_py(self, project_function, test_utils, caplog):
        _, project = project_function.activate()
        test_name = 'test_one'
        test_utils.create_test(project, [], test_name)
        commands.run_command(project=project, test_query='test_one.py')
        records = caplog.records
        assert records[0].message == 'Test execution started: {}'.format(test_name)
        assert records[4].message == 'Test Result: SUCCESS'
        # the execution report is created for suite
        path = os.path.join(project_function.path, 'reports', 'single_tests', 'test_one')
        assert os.path.isdir(path)
        # only one timestamp
        assert len(os.listdir(path)) == 1

    @pytest.mark.slow
    def test_golem_run_test_in_folder(self, project_function, test_utils, caplog):
        _, project = project_function.activate()
        test_utils.create_test(project, ['folder'], 'test_one')
        commands.run_command(project=project, test_query='folder.test_one')
        records = caplog.records
        assert records[0].message == 'Test execution started: folder.test_one'
        assert records[4].message == 'Test Result: SUCCESS'

    @pytest.mark.slow
    def test_golem_run_test_py_in_folder(self, project_function, test_utils, caplog):
        _, project = project_function.activate()
        test_utils.create_test(project, ['folder'], 'test_one')
        commands.run_command(project=project, test_query='folder/test_one.py')
        records = caplog.records
        assert records[0].message == 'Test execution started: folder.test_one'
        assert records[4].message == 'Test Result: SUCCESS'

    @pytest.mark.slow
    @pytest.mark.skipif("os.name != 'nt'")
    def test_golem_run_test_py_in_folder_windows_path(self, project_function, test_utils,
                                                      caplog):
        _, project = project_function.activate()
        test_utils.create_test(project, ['folder'], 'test_one')
        commands.run_command(project=project, test_query='folder\\test_one.py')
        records = caplog.records
        assert records[0].message == 'Test execution started: folder.test_one'
        assert records[4].message == 'Test Result: SUCCESS'

    @pytest.mark.slow
    def test_golem_run_directory(self, project_function, test_utils):
        _, project = project_function.activate()
        test_utils.create_test(project, [], 'test_one')
        test_utils.create_test(project, ['foo'], 'test_two')
        test_utils.create_test(project, ['foo'], 'test_three')
        test_utils.create_test(project, ['foo', 'bar'], 'test_four')
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
        test_utils.create_test(project, [], 'test_one')
        test_utils.create_test(project, ['foo'], 'test_two')
        test_utils.create_test(project, ['foo', 'bar'], 'test_three')
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
    def test_exit_code_one_on_test_failure_when_using_single_processing_capabilities(self, project_function, test_utils):
        _, project = project_function.activate()
        test_utils.create_test(project, [], 'test_one', content=self.content)
        test_utils.create_test(project, [], 'test_two')

        with pytest.raises(SystemExit) as wrapped_execution:
            commands.run_command(project=project, test_query='.', processes=1)

        assert wrapped_execution.value.code == 1

    @pytest.mark.slow
    def test_exit_code_one_on_test_failure_when_using_multi_processing_capabilities(self, project_function, test_utils):
        _, project = project_function.activate()
        test_utils.create_test(project, [], 'test_one', content=self.content)
        test_utils.create_test(project, [], 'test_two')

        with pytest.raises(SystemExit) as wrapped_execution:
            commands.run_command(project=project, test_query='.', processes=2)

        assert wrapped_execution.value.code == 1
