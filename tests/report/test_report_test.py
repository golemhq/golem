import json
import os

from golem.core import utils
from golem.test_runner import test_runner
from golem.test_runner.conf import ResultsEnum

from golem.report.execution_report import create_execution_directory
from golem.report import test_report
from golem.report.test_report import get_test_file_report_json
from golem.report.test_report import get_test_debug_log
from golem.report.test_report import create_test_file_report_dir
from golem.report.test_report import generate_report


class TestGetTestFileReportJson:

    def test_get_test_file_report_json(self, project_class, test_utils):
        _, project = project_class.activate()
        exc = test_utils.execute_random_suite(project)
        test_file = exc['exec_data']['tests'][0]['test_file']
        test_set = exc['exec_data']['tests'][0]['set_name']

        test_data = get_test_file_report_json(project, exc['suite_name'], exc['timestamp'],
                                              test_file, test_set)

        assert len(test_data) == 1
        assert isinstance(test_data[0], dict)
        assert test_data[0]['test_file'] == test_file
        assert test_data[0]['test'] == 'test'
        assert test_data[0]['set_name'] == ''
        assert len(test_data[0]) == 12

    def test_report_does_not_exist(self, project_class, test_utils):
        _, project = project_class.activate()
        test_data = get_test_file_report_json(project, 'execution', 'timestamp', 'test_name')

        assert test_data is None


# class TestGetTestCaseData:
#
#     def test_get_test_case_data(self, project_class, test_utils):
#         _, project = project_class.activate()
#         exc = test_utils.execute_random_suite(project)
#         test_name = exc['exec_data']['tests'][0]['name']
#         test_set = exc['exec_data']['tests'][0]['test_set']
#
#         test_data = get_test_case_data(project, test_name, exc['suite_name'],
#                                        exc['timestamp'], test_set)
#
#         assert test_data['name'] == exc['tests'][0]
#         assert isinstance(test_data['debug_log'], list) and len(test_data['debug_log'])
#         assert isinstance(test_data['info_log'], list) and len(test_data['info_log'])
#         assert test_data['has_finished'] is True


class TestTestFileReportDir:

    def test_create_test_file_report_dir_without_setname(self, project_session):
        testdir, project = project_session.activate()
        suite = 'suite1'
        timestamp = '1.2.3.4'
        test = 'test1'
        path = test_report.test_file_report_dir(test, project, suite, timestamp)
        expected = os.path.join(testdir, 'projects', project, 'reports', suite, timestamp, test)
        assert path == expected

    def test_create_test_file_report_dir_with_setname(self, project_session):
        testdir, project = project_session.activate()
        suite = 'suite1'
        timestamp = '1.2.3.4'
        test = 'test1'
        test_set = 'test_set1'
        path = test_report.test_file_report_dir(test, project, suite, timestamp, test_set)
        expected = os.path.join(testdir, 'projects', project, 'reports', suite, timestamp,
                                '{}.{}'.format(test, test_set))
        assert path == expected


class TestTestFunctionReportDir:

    def test_create_test_file_report_dir_without_setname(self, project_session):
        testdir, project = project_session.activate()
        suite = 'suite1'
        timestamp = '1.2.3.4'
        test_file = 'test1'
        test_function = 'function1'
        path = test_report.test_function_report_dir(project, suite, timestamp, test_file, test_function)
        test_file_path = test_report.test_file_report_dir(test_file, project, suite, timestamp)
        expected = os.path.join(test_file_path, test_function)
        assert path == expected


class TestGetTestLog:

    def test_get_test_x_log(self, project_class, test_utils):
        _, project = project_class.activate()
        exc = test_utils.execute_random_suite(project)
        suite_name = exc['suite_name']
        test_file = exc['exec_data']['tests'][0]['test_file']
        set_name = exc['exec_data']['tests'][0]['set_name']

        log = get_test_debug_log(project, suite_name, exc['timestamp'], test_file, set_name)

        assert 'root INFO Test execution started: {}'.format(test_file) in log[0]

        # inexistent test set
        log = get_test_debug_log(project, suite_name, exc['timestamp'], test_file,
                                 'inexistent_test_set')
        assert log is None

        # inexistent test
        log = get_test_debug_log(project, suite_name, exc['timestamp'],
                                 'inexistent_test_name', set_name)
        assert log is None


class TestCreateReportDirectory:

    def test_create_report_directory_test_without_set(self, project_session):
        testdir, project = project_session.activate()
        timestamp = utils.get_timestamp()
        test_name = 'testing_report_001'
        exec_dir = create_execution_directory(project, test_name, timestamp)
        directory = create_test_file_report_dir(exec_dir, test_name, '')
        assert os.path.isdir(directory)


class TestInitializeTestFileReport:

    def test_initialize_test_file_report(self, project_session, test_utils):
        _, project = project_session.activate()
        # create a test
        test_file = test_utils.random_string()
        content = 'def test_one(data):\n' \
                  '    pass\n' \
                  'def test_two(data):\n' \
                  '    pass'
        test_utils.create_test(project, test_file, content)
        # create test file reportdir
        execution = test_file
        timestamp = utils.get_timestamp()
        exec_dir = create_execution_directory(project, test_file, timestamp)
        test_file_reportdir = create_test_file_report_dir(exec_dir, test_file, '')
        # initialize report for test file
        test_report.initialize_test_file_report(
            test_file, ['test_one', 'test_two'], '', test_file_reportdir)
        test_file_report = test_report.get_test_file_report_json(
            project, execution, timestamp, test_file)
        assert len(test_file_report) == 2
        assert any(t['test'] == 'test_one' and t['result'] == ResultsEnum.PENDING for t in test_file_report)
        assert any(t['test'] == 'test_two' and t['result'] == ResultsEnum.PENDING for t in test_file_report)


class TestGenerateReport:

    def test_generate_report_with_env(self, project_session):
        _, project = project_session.activate()
        timestamp = utils.get_timestamp()
        test_name = 'testing_report_003'
        suite_name = 'suite_foo_003'
        exec_dir = create_execution_directory(project, suite_name, timestamp)
        report_dir = create_test_file_report_dir(exec_dir, test_name, '')
        test_data = {
            'env': {
                'name': 'env01',
                'url': '1.1.1.1'
            },
            'var2': 'value2'
        }
        test_data = test_runner.Data(test_data)
        result = {
            'name': 'test_function',
            'set_name': 'set_001',
            'start_time': '',
            'end_time': '',
            'report_directory': '',
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
            'browser_capabilities': '',
        }
        generate_report(test_name, result, test_data, report_dir)
        path = os.path.join(report_dir, 'report.json')
        with open(path) as report_file:
            actual = json.load(report_file)
            actual = actual[0]
            assert len(actual.items()) == 12
            assert actual['test_file'] == test_name
            assert actual['test'] == 'test_function'
            assert actual['result'] == 'success'
            assert actual['steps'][0]['message'] == 'step1'
            assert actual['steps'][1]['message'] == 'step2'
            assert actual['description'] == 'description of the test'
            assert actual['errors'] == []
            assert actual['elapsed_time'] == 22.22
            assert actual['timestamp'] == '2018.02.04.02.16.42.729'
            assert actual['browser'] == 'chrome'
            assert actual['environment'] == 'env01'
            assert actual['set_name'] == 'set_001'
            test_data_a = "{'url': '1.1.1.1', 'name': 'env01'}"
            test_data_b = "{'name': 'env01', 'url': '1.1.1.1'}"
            assert actual['test_data']['env'] in [test_data_a, test_data_b]
            assert actual['test_data']['var2'] == "'value2'"
