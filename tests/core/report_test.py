import os
import json

from golem.core import report, utils
from golem.test_runner import test_runner


class TestCreateExecutionDirectoryTest:

    def test_create_execution_directory_test(self, project_session):
        testdir, project = project_session.activate()
        timestamp = utils.get_timestamp()
        test_name = 'test_execution_directory'
        directory = report.create_execution_directory(project, timestamp, test_name=test_name)
        path = os.path.join(project_session.path, 'reports', 'single_tests', test_name, timestamp)
        assert os.path.isdir(path)
        assert directory == path

    def test_create_execution_directory_test_parents(self, project_session):
        testdir, project = project_session.activate()
        timestamp = utils.get_timestamp()
        test_name = 'a.b.test_execution_directory'
        directory = report.create_execution_directory(project, timestamp, test_name=test_name)
        path = os.path.join(project_session.path, 'reports', 'single_tests', test_name, timestamp)
        assert os.path.isdir(path)
        assert directory == path

    def test_create_execution_directory_suite(self, project_session):
        testdir, project = project_session.activate()
        timestamp = utils.get_timestamp()
        suite_name = 'suite_execution_directory'
        directory = report.create_execution_directory(project, timestamp, suite_name=suite_name)
        path = os.path.join(project_session.path, 'reports', suite_name, timestamp)
        assert os.path.isdir(path)
        assert directory == path

    def test_create_execution_directory_suite_parents(self, project_session):
        testdir, project = project_session.activate()
        timestamp = utils.get_timestamp()
        suite_name = 'a.b.suite_execution_directory'
        directory = report.create_execution_directory(project, timestamp, suite_name=suite_name)
        path = os.path.join(project_session.path, 'reports', suite_name, timestamp)
        assert os.path.isdir(path)
        assert directory == path


class TestCreateReportDirectory:

    def test_create_report_directory_test(self, project_session):
        testdir, project = project_session.activate()
        timestamp = utils.get_timestamp()
        test_name = 'testing_report_001'
        exec_dir = report.create_execution_directory(project, timestamp, test_name=test_name)
        directory = report.create_report_directory(exec_dir, test_name, is_suite=False)
        assert os.path.isdir(directory)

    def test_create_report_directory_suite(self, project_session):
        testdir, project = project_session.activate()
        timestamp = utils.get_timestamp()
        test_name = 'testing_report_002'
        exec_dir = report.create_execution_directory(project, timestamp, test_name=test_name)
        directory = report.create_report_directory(exec_dir, test_name, is_suite=True)
        assert os.path.isdir(directory)


class TestGenerateReport:

    def test_generate_report_with_env(self, project_session):
        _, project = project_session.activate()
        timestamp = utils.get_timestamp()
        test_name = 'testing_report_003'
        exec_dir = report.create_execution_directory(project, timestamp, test_name=test_name)
        report_dir = report.create_report_directory(exec_dir, test_name, is_suite=True)
        test_data = {
            'env': {
                'name': 'env01',
                'url': '1.1.1.1'
            },
            'var2': 'value2'
        }
        test_data = test_runner.Data(test_data)
        result = {
            'result': 'success',
            'errors': [],
            'description': 'description of the test',
            'steps': [
                {'message': 'step1', 'screenshot': None, 'error': None},
                {'message': 'step2', 'screenshot': None, 'error': None}
            ],
            'test_elapsed_time': 22.22,
            'test_timestamp': '2018.02.04.02.16.42.729',
            'browser': 'chrome',
            'browser_full_name': '',
            'set_name': 'set_001',
        }
        report.generate_report(report_dir, test_name, test_data, result)
        path = os.path.join(report_dir, 'report.json')
        with open(path) as report_file:
            actual = json.load(report_file)
            assert len(actual.items()) == 11
            assert actual['test_case'] == test_name
            assert actual['result'] == 'success'
            assert actual['steps'][0]['message'] == 'step1'
            assert actual['steps'][1]['message'] == 'step2'
            assert actual['description'] == 'description of the test'
            assert actual['errors'] == []
            assert actual['test_elapsed_time'] == 22.22
            assert actual['test_timestamp'] == '2018.02.04.02.16.42.729'
            assert actual['browser'] == 'chrome'
            assert actual['environment'] == 'env01'
            assert actual['set_name'] == 'set_001'
            test_data_a = "{'url': '1.1.1.1', 'name': 'env01'}"
            test_data_b = "{'name': 'env01', 'url': '1.1.1.1'}"
            assert actual['test_data']['env'] in [test_data_a, test_data_b]
            assert actual['test_data']['var2'] == "'value2'"
