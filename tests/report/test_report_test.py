import json
import os

from golem.core import utils
from golem.test_runner import test_runner

from golem.report.execution_report import create_execution_directory
from golem.report.execution_report import create_execution_dir_single_test
from golem.report import test_report
from golem.report.test_report import get_test_case_data
from golem.report.test_report import get_test_debug_log
from golem.report.test_report import create_report_directory
from golem.report.test_report import generate_report


class TestGetTestCaseData:

    def test_get_test_case_data(self, project_class, test_utils):
        _, project = project_class.activate()
        exc = test_utils.execute_random_suite(project)
        test_name = exc['exec_data']['tests'][0]['name']
        test_set = exc['exec_data']['tests'][0]['test_set']

        test_data = get_test_case_data(project, test_name, exc['suite_name'],
                                       exc['timestamp'], test_set)

        assert test_data['name'] == exc['tests'][0]
        assert isinstance(test_data['debug_log'], list) and len(test_data['debug_log'])
        assert isinstance(test_data['info_log'], list) and len(test_data['info_log'])
        assert test_data['has_finished'] is True


class TestTestReportDirectory:

    def test_test_report_directory(self, project_session):
        testdir, project = project_session.activate()
        suite = 'suite1'
        timestamp = '1.2.3.4'
        test = 'test1'
        test_set = 'test_set1'
        path = test_report.test_report_directory(project, suite, timestamp, test, test_set)
        expected = os.path.join(testdir, 'projects', project, 'reports', suite, timestamp,
                                test, test_set)
        assert path == expected


class TestTestReportDirectorySingleTest:

    def test_test_report_directory_single_test(self, project_session):
        testdir, project = project_session.activate()
        timestamp = '1.2.3.4'
        test = 'test1'
        test_set = 'test_set1'
        path = test_report.test_report_directory_single_test(project, test, timestamp, test_set)
        expected = os.path.join(testdir, 'projects', project, 'reports', 'single_tests',
                                test, timestamp, test_set)
        assert path == expected


class TestGetTestLog:

    def test_get_test_x_log(self, project_class, test_utils):
        _, project = project_class.activate()
        exc = test_utils.execute_random_suite(project)
        test_name = exc['exec_data']['tests'][0]['name']
        test_set = exc['exec_data']['tests'][0]['test_set']

        log = get_test_debug_log(project, exc['timestamp'], test_name, test_set,
                                 suite=exc['suite_name'])

        assert 'root DEBUG test does not have setup function' in log

        # inexistent test set
        log = get_test_debug_log(project, exc['timestamp'], test_name,
                                 'inexistent_test_set', suite=exc['suite_name'])
        assert log is None

        # inexistent test
        log = get_test_debug_log(project, exc['timestamp'], 'inexistent_test_name',
                                 test_set, suite=exc['suite_name'])
        assert log is None


class TestCreateReportDirectory:

    def test_create_report_directory_test(self, project_session):
        testdir, project = project_session.activate()
        timestamp = utils.get_timestamp()
        test_name = 'testing_report_001'
        exec_dir = create_execution_dir_single_test(project, test_name, timestamp)
        directory = create_report_directory(exec_dir, test_name, is_suite=False)
        assert os.path.isdir(directory)

    def test_create_report_directory_suite(self, project_session):
        testdir, project = project_session.activate()
        timestamp = utils.get_timestamp()
        suite_name = 'suite_foo_002'
        test_name = 'testing_report_002'
        exec_dir = create_execution_directory(project, suite_name, timestamp)
        directory = create_report_directory(exec_dir, test_name, is_suite=True)
        assert os.path.isdir(directory)


class TestGenerateReport:

    def test_generate_report_with_env(self, project_session):
        _, project = project_session.activate()
        timestamp = utils.get_timestamp()
        test_name = 'testing_report_003'
        suite_name = 'suite_foo_003'
        exec_dir = create_execution_directory(project, suite_name, timestamp)
        report_dir = create_report_directory(exec_dir, test_name, is_suite=True)
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
        generate_report(report_dir, test_name, test_data, result)
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
