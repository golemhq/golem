import json
import os

from golem.core import utils
from golem.core.report import create_report_directory, generate_report
from golem.test_runner import test_runner
from golem.gui.report_parser import generate_junit_report
from golem.test_runner.execution_runner import define_browsers
from golem.gui.gui_utils import generate_html_report

from golem.report import report
from golem.report.execution_report import generate_execution_report, get_execution_data, _parse_execution_data, save_execution_json_report, create_execution_directory


def execute_random_suite(project, test_utils):
    """
    """
    tests = ['test1']
    suite = test_utils.random_string()
    for test in tests:
        test_utils.create_test(project, name=test)
    test_utils.create_suite(project, name=suite, tests=tests)
    execution = execute_suite(project, suite, test_utils)
    execution['tests'] = tests
    return execution


def execute_suite(project, suite, test_utils):
    """
    """
    timestamp = test_utils.run_suite(project, suite)
    exec_data = get_execution_data(project=project, suite=suite, execution=timestamp)
    exec_dir = report.suite_execution_path(project, suite, timestamp)
    return {
        'exec_dir': exec_dir,
        'report_path': os.path.join(exec_dir, 'report.json'),
        'suite_name': suite,
        'timestamp': timestamp,
        'exec_data': exec_data
    }


class TestGetLastExecution:

    def test_get_last_executions(self, project_function, test_utils):
        _, project = project_function.activate()

        # suite does not exist
        last_exec = report.get_last_executions([project], 'suite_does_not_exist')
        assert last_exec[project] == {}

        # suite with no executions
        suite_name = 'suite1'
        test_utils.create_test(project, name='test1')
        test_utils.create_suite(project, name=suite_name, tests=['test1'])

        assert last_exec[project] == {}

        # suite with one execution
        timestamp = test_utils.run_suite(project, suite_name)
        last_exec = report.get_last_executions([project], suite_name)
        assert last_exec[project] == {suite_name: [timestamp]}

        # multiple executions
        timestamps = [timestamp]
        timestamps.append(test_utils.run_suite(project, suite_name))
        timestamps.append(test_utils.run_suite(project, suite_name))
        last_exec = report.get_last_executions([project], suite_name, limit=2)
        assert len(last_exec[project][suite_name]) == 2
        assert last_exec[project][suite_name][0] == timestamps[1]
        assert last_exec[project][suite_name][1] == timestamps[2]


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
        exec_dir = report.suite_execution_path(project, suite_name, timestamp)

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
        exec_dir = report.suite_execution_path(project, suite_name, timestamp)
        report_path = os.path.join(exec_dir, 'report.json')
        os.remove(report_path)

        exec_data = get_execution_data(project=project, suite=suite_name, execution=timestamp)

        assert len(exec_data['tests']) == 1
        assert exec_data['tests'][0]['name'] == 'test1'
        assert exec_data['total_tests'] == 1
        assert exec_data['has_finished'] is False


class TestGetTestCaseData:

    def test_get_test_case_data(self, project_class, test_utils):
        _, project = project_class.activate()
        exec = execute_random_suite(project, test_utils)
        test_name = exec['exec_data']['tests'][0]['name']
        test_set = exec['exec_data']['tests'][0]['test_set']

        test_data = report.get_test_case_data(project, test_name, exec['suite_name'],
                                              exec['timestamp'], test_set)

        assert test_data['name'] == exec['tests'][0]
        assert isinstance(test_data['debug_log'], list) and len(test_data['debug_log'])
        assert isinstance(test_data['info_log'], list) and len(test_data['info_log'])
        assert test_data['has_finished'] is True


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


class TestDeleteExecution:

    def test_delete_execution(self, project_class, test_utils):
        _, project = project_class.activate()
        execution = execute_random_suite(project, test_utils)
        assert os.path.isdir(execution['exec_dir'])

        errors = report.delete_execution(project, execution['suite_name'], execution['timestamp'])

        assert errors == []
        assert not os.path.isdir(execution['exec_dir'])


class TestGenerateExecutionReport:

    def test_generate_execution_report(self, project_class, test_utils):
        _, project = project_class.activate()
        execution = execute_random_suite(project, test_utils)
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


class TestGenerateJunitReport:

    def test_generate_junit_report(self, project_class, test_utils):
        _, project = project_class.activate()
        execution = execute_random_suite(project, test_utils)

        xml = generate_junit_report(execution['exec_dir'], execution['suite_name'], execution['timestamp'])

        suite_name = execution['suite_name']
        suite_time = execution['exec_data']['net_elapsed_time']
        timestamp = execution['timestamp']
        test_name = execution['exec_data']['tests'][0]['name']
        test_set = execution['exec_data']['tests'][0]['test_set']
        test_time = execution['exec_data']['tests'][0]['test_elapsed_time']
        class_name = '{}.{}'.format(test_name, test_set)
        expected = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                    '<testsuites errors="0" failures="0" name="{0}" tests="1" time="{1}">\n'
                    '    <testsuite errors="0" failures="0" name="{0}" tests="1" time="{1}" timestamp="{2}">\n'
                    '        <testcase classname="{3}" name="{4}" status="success" time="{5}"/>\n'
                    '    </testsuite>\n'
                    '</testsuites>\n'.format(suite_name, suite_time, timestamp, class_name, test_name, test_time).encode())
        assert xml == expected
        xml_path = os.path.join(execution['exec_dir'], 'report.xml')
        assert os.path.isfile(xml_path)


class TestCreateExecutionDirectoryTest:

    def test_create_execution_directory_test(self, project_session):
        testdir, project = project_session.activate()
        timestamp = utils.get_timestamp()
        test_name = 'test_execution_directory'
        directory = create_execution_directory(project, timestamp, test_name=test_name)
        path = os.path.join(project_session.path, 'reports', 'single_tests', test_name, timestamp)
        assert os.path.isdir(path)
        assert directory == path

    def test_create_execution_directory_test_parents(self, project_session):
        testdir, project = project_session.activate()
        timestamp = utils.get_timestamp()
        test_name = 'a.b.test_execution_directory'
        directory = create_execution_directory(project, timestamp, test_name=test_name)
        path = os.path.join(project_session.path, 'reports', 'single_tests', test_name, timestamp)
        assert os.path.isdir(path)
        assert directory == path

    def test_create_execution_directory_suite(self, project_session):
        testdir, project = project_session.activate()
        timestamp = utils.get_timestamp()
        suite_name = 'suite_execution_directory'
        directory = create_execution_directory(project, timestamp, suite_name=suite_name)
        path = os.path.join(project_session.path, 'reports', suite_name, timestamp)
        assert os.path.isdir(path)
        assert directory == path

    def test_create_execution_directory_suite_parents(self, project_session):
        testdir, project = project_session.activate()
        timestamp = utils.get_timestamp()
        suite_name = 'a.b.suite_execution_directory'
        directory = create_execution_directory(project, timestamp, suite_name=suite_name)
        path = os.path.join(project_session.path, 'reports', suite_name, timestamp)
        assert os.path.isdir(path)
        assert directory == path


class TestCreateReportDirectory:

    def test_create_report_directory_test(self, project_session):
        testdir, project = project_session.activate()
        timestamp = utils.get_timestamp()
        test_name = 'testing_report_001'
        exec_dir = create_execution_directory(project, timestamp, test_name=test_name)
        directory = create_report_directory(exec_dir, test_name, is_suite=False)
        assert os.path.isdir(directory)

    def test_create_report_directory_suite(self, project_session):
        testdir, project = project_session.activate()
        timestamp = utils.get_timestamp()
        test_name = 'testing_report_002'
        exec_dir = create_execution_directory(project, timestamp, test_name=test_name)
        directory = create_report_directory(exec_dir, test_name, is_suite=True)
        assert os.path.isdir(directory)


class TestGenerateReport:

    def test_generate_report_with_env(self, project_session):
        _, project = project_session.activate()
        timestamp = utils.get_timestamp()
        test_name = 'testing_report_003'
        exec_dir = create_execution_directory(project, timestamp, test_name=test_name)
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


class TestGenerateHTMLReport:

    def test_generate_html_report(self, project_class, test_utils):
        _, project = project_class.activate()
        execution = execute_random_suite(project, test_utils)

        html = generate_html_report(project, execution['suite_name'], execution['timestamp'])

        html_path = os.path.join(execution['exec_dir'], 'report.html')
        assert os.path.isfile(html_path)
        with open(html_path) as f:
            assert f.read() == html
