import json
import os

from golem.core import utils
from golem.execution_runner.execution_runner import define_browsers
from golem.report.execution_report import generate_execution_report
from golem.report.execution_report import get_execution_data
from golem.report.execution_report import _parse_execution_data
from golem.report.execution_report import save_execution_json_report
from golem.report.execution_report import create_execution_directory
from golem.report.execution_report import create_execution_dir_single_test
from golem.report.execution_report import suite_execution_path


class TestParseExecutionData:

    def test_parse_execution_data(self, project_function, test_utils):
        _, project = project_function.activate()
        suite_name = 'suite1'
        test_utils.create_test(project, name='test1')
        test_utils.create_suite(project, name=suite_name, tests=['test1'])
        timestamp = test_utils.run_suite(project, suite_name)

        exec_data = _parse_execution_data(project=project, suite=suite_name, execution=timestamp)

        assert len(exec_data['tests']) == 1
        assert exec_data['tests'][0]['name'] == 'test1'
        assert exec_data['total_tests'] == 1
        assert exec_data['totals_by_result'] == {'success': 1}
        assert exec_data['has_finished'] is False
        assert exec_data['params']['browsers'] == []
        assert exec_data['params']['processes'] is None
        assert exec_data['params']['environments'] == []
        assert exec_data['params']['tags'] == []
        assert exec_data['params']['remote_url'] == ''

    def test_parse_execution_data_exec_dir(self, project_function, test_utils):
        _, project = project_function.activate()
        suite_name = 'suite1'
        test_utils.create_test(project, name='test1')
        test_utils.create_suite(project, name=suite_name, tests=['test1'])
        timestamp = test_utils.run_suite(project, suite_name)
        exec_dir = suite_execution_path(project, suite_name, timestamp)

        exec_data = _parse_execution_data(execution_directory=exec_dir)

        assert len(exec_data['tests']) == 1
        assert exec_data['tests'][0]['name'] == 'test1'
        assert exec_data['total_tests'] == 1


class TestGetExecutionData:

    def test_get_execution_data_from_report_json(self, project_function, test_utils):
        _, project = project_function.activate()
        suite_name = 'suite1'
        test_utils.create_test(project, name='test1')
        test_utils.create_suite(project, name=suite_name, tests=['test1'])
        timestamp = test_utils.run_suite(project, suite_name)

        exec_data = get_execution_data(project=project, suite=suite_name, execution=timestamp)

        assert len(exec_data['tests']) == 1
        assert exec_data['tests'][0]['name'] == 'test1'
        assert exec_data['total_tests'] == 1
        assert exec_data['has_finished'] is True

    def test_get_execution_data_unfinished_execution(self, project_function, test_utils):
        _, project = project_function.activate()
        suite_name = 'suite1'
        test_utils.create_test(project, name='test1')
        test_utils.create_suite(project, name=suite_name, tests=['test1'])
        timestamp = test_utils.run_suite(project, suite_name)
        exec_dir = suite_execution_path(project, suite_name, timestamp)
        report_path = os.path.join(exec_dir, 'report.json')
        os.remove(report_path)

        exec_data = get_execution_data(project=project, suite=suite_name, execution=timestamp)

        assert len(exec_data['tests']) == 1
        assert exec_data['tests'][0]['name'] == 'test1'
        assert exec_data['total_tests'] == 1
        assert exec_data['has_finished'] is False


class TestGenerateExecutionReport:

    def test_generate_execution_report(self, project_class, test_utils):
        _, project = project_class.activate()
        execution = test_utils.execute_random_suite(project)
        os.remove(execution['report_path'])
        elapsed_time = 1122
        browsers = define_browsers(['chrome'], [], ['chrome'])
        processes = 2
        envs = ['test', 'staging']
        tags = ['foo', 'bar']
        remote_url = 'https://foo.bar'

        reprt = generate_execution_report(execution['exec_dir'], elapsed_time,
                                          browsers, processes, envs, tags, remote_url)

        expected_params = {
            'browsers': [{'name': 'chrome', 'full_name': None, 'remote': False, 'capabilities': {}}],
            'processes': 2,
            'environments': ['test', 'staging'],
            'tags': ['foo', 'bar'],
            'remote_url': ''
        }
        assert reprt['params'] == expected_params
        assert os.path.isfile(execution['report_path'])


class TestSaveExecutionJsonReport:

    def test_save_execution_json_report(self, dir_function):
        folder = 'folder1'
        reportdir = os.path.join(dir_function.path, folder)
        os.mkdir(reportdir)
        sample_data = {"json": True}

        # default name
        save_execution_json_report(sample_data, reportdir)

        report_path = os.path.join(reportdir, 'report.json')
        assert os.path.isfile(report_path)
        with open(report_path) as f:
            assert json.load(f) == sample_data

        # custom name
        save_execution_json_report(sample_data, reportdir, report_name='foo')

        report_path = os.path.join(reportdir, 'foo.json')
        assert os.path.isfile(report_path)
        with open(report_path) as f:
            assert json.load(f) == sample_data


class TestCreateExecutionDirectoryTest:

    def test_create_execution_directory_suite(self, project_session):
        testdir, project = project_session.activate()
        timestamp = utils.get_timestamp()
        suite_name = 'suite_execution_directory'
        directory = create_execution_directory(project, suite_name, timestamp)
        path = os.path.join(project_session.path, 'reports', suite_name, timestamp)
        assert os.path.isdir(path)
        assert directory == path

    def test_create_execution_directory_suite_parents(self, project_session):
        testdir, project = project_session.activate()
        timestamp = utils.get_timestamp()
        suite_name = 'a.b.suite_execution_directory'
        directory = create_execution_directory(project, suite_name, timestamp)
        path = os.path.join(project_session.path, 'reports', suite_name, timestamp)
        assert os.path.isdir(path)
        assert directory == path


class TestCreateExecutionDirectorySingleTest:

    def test_create_execution_dir_single_test(self, project_session, test_utils):
        _, project = project_session.activate()
        timestamp = utils.get_timestamp()
        test_name = test_utils.random_string()
        directory = create_execution_dir_single_test(project, test_name, timestamp)
        path = os.path.join(project_session.path, 'reports', 'single_tests', test_name, timestamp)
        assert os.path.isdir(path)
        assert directory == path

    def test_create_execution_dir_single_test_parents(self, project_session, test_utils):
        _, project = project_session.activate()
        timestamp = utils.get_timestamp()
        test_name = 'foo.bar.{}'.format(test_utils.random_string())
        directory = create_execution_dir_single_test(project, test_name, timestamp)
        path = os.path.join(project_session.path, 'reports', 'single_tests', test_name, timestamp)
        assert os.path.isdir(path)
        assert directory == path
