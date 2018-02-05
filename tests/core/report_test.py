import os
import json

from golem.core import report, utils
from golem.test_runner import test_runner

from tests.fixtures import testdir_fixture, permanent_project_fixture


class Test_create_execution_directory:

    def test_create_execution_directory_test(self, permanent_project_fixture):
        project = permanent_project_fixture['name']
        testdir = permanent_project_fixture['testdir']
        timestamp = utils.get_timestamp()
        test_name = 'test_execution_directory'
        directory = report.create_execution_directory(testdir, project, timestamp,
                                                      test_name=test_name)
        path = os.path.join(testdir, 'projects', project, 'reports',
                            'single_tests', test_name, timestamp)
        assert os.path.isdir(path)
        assert directory == path


    def test_create_execution_directory_test_parents(self, permanent_project_fixture):
        project = permanent_project_fixture['name']
        testdir = permanent_project_fixture['testdir']
        timestamp = utils.get_timestamp()
        test_name = 'a.b.test_execution_directory'
        directory = report.create_execution_directory(testdir, project, timestamp,
                                                      test_name=test_name)
        path = os.path.join(testdir, 'projects', project, 'reports',
                            'single_tests', test_name, timestamp)
        assert os.path.isdir(path)
        assert directory == path


    def test_create_execution_directory_suite(self, permanent_project_fixture):
        project = permanent_project_fixture['name']
        testdir = permanent_project_fixture['testdir']
        timestamp = utils.get_timestamp()
        suite_name = 'suite_execution_directory'
        directory = report.create_execution_directory(testdir, project, timestamp,
                                                      suite_name=suite_name)
        path = os.path.join(testdir, 'projects', project, 'reports',
                            suite_name, timestamp)
        assert os.path.isdir(path)
        assert directory == path


    def test_create_execution_directory_suite_parents(self, permanent_project_fixture):
        project = permanent_project_fixture['name']
        testdir = permanent_project_fixture['testdir']
        timestamp = utils.get_timestamp()
        suite_name = 'a.b.suite_execution_directory'
        directory = report.create_execution_directory(testdir, project, timestamp,
                                          suite_name=suite_name)
        path = os.path.join(testdir, 'projects', project, 'reports',
                            suite_name, timestamp)
        assert os.path.isdir(path)
        assert directory == path


class Test_create_report_directory:

    def test_create_report_directory_test(self, permanent_project_fixture):
        project = permanent_project_fixture['name']
        testdir = permanent_project_fixture['testdir']
        timestamp = utils.get_timestamp()
        test_name = 'testing_report_001'
        exec_dir = report.create_execution_directory(testdir, project, timestamp,
                                                     test_name=test_name)
        directory = report.create_report_directory(exec_dir, test_name,
                                                   is_suite=False)
        assert os.path.isdir(directory)


    def test_create_report_directory_suite(self, permanent_project_fixture):
        project = permanent_project_fixture['name']
        testdir = permanent_project_fixture['testdir']
        timestamp = utils.get_timestamp()
        test_name = 'testing_report_002'
        exec_dir = report.create_execution_directory(testdir, project, timestamp,
                                                     test_name=test_name)
        directory = report.create_report_directory(exec_dir, test_name,
                                                   is_suite=True)
        assert os.path.isdir(directory)


class Test_generate_report:

    def test_generate_report(self, permanent_project_fixture):
        project = permanent_project_fixture['name']
        testdir = permanent_project_fixture['testdir']
        timestamp = utils.get_timestamp()
        test_name = 'testing_report_002'
        exec_dir = report.create_execution_directory(testdir, project, timestamp,
                                                     test_name=test_name)
        report_dir = report.create_report_directory(exec_dir, test_name,
                                                    is_suite=True)
        test_data = {
            'var1': 'value1',
            'var2': 'value2'
        }
        result = {
            'result': 'pass',
            'error': '',
            'description': 'description of the test',
            'steps': ['step1', 'step2'],
            'test_elapsed_time': 22.22,
            'test_timestamp': '2018.02.04.02.16.42.729',
            'browser': 'chrome',
            'browser_full_name': '',
            'set_name': 'set_001',
        }
        report.generate_report(report_dir, test_name, test_data, result)
        expected = {
            'test_case': test_name,
            'result': 'pass',
            'steps': ['step1', 'step2'],
            'description': 'description of the test',
            'error': '',
            'short_error': '',
            'test_elapsed_time': 22.22,
            'test_timestamp': '2018.02.04.02.16.42.729',
            'browser': 'chrome',
            'environment': '',
            'set_name': 'set_001',
            'test_data': {
                'var1': "'value1'",
                'var2': "'value2'"
            }
        }
        path = os.path.join(report_dir, 'report.json')
        with open(path) as report_file:
            actual = json.load(report_file)
            assert actual == expected


    def test_generate_report_with_env(self, permanent_project_fixture):
        project = permanent_project_fixture['name']
        testdir = permanent_project_fixture['testdir']
        timestamp = utils.get_timestamp()
        test_name = 'testing_report_003'
        exec_dir = report.create_execution_directory(testdir, project, timestamp,
                                                     test_name=test_name)
        report_dir = report.create_report_directory(exec_dir, test_name,
                                                    is_suite=True)
        test_data = {
            'env': {
                'name': 'env01',
                'url': '1.1.1.1'
            },
            'var2': 'value2'
        }
        test_data = test_runner.Data(test_data)

        result = {
            'result': 'pass',
            'error': '',
            'description': 'description of the test',
            'steps': ['step1', 'step2'],
            'test_elapsed_time': 22.22,
            'test_timestamp': '2018.02.04.02.16.42.729',
            'browser': 'chrome',
            'browser_full_name': '',
            'set_name': 'set_001',
        }
        report.generate_report(report_dir, test_name, test_data, result)
        expected = {
            'test_case': test_name,
            'result': 'pass',
            'steps': ['step1', 'step2'],
            'description': 'description of the test',
            'error': '',
            'short_error': '',
            'test_elapsed_time': 22.22,
            'test_timestamp': '2018.02.04.02.16.42.729',
            'browser': 'chrome',
            'environment': 'env01',
            'set_name': 'set_001',
            'test_data': {
                'env': "{'name': 'env01', 'url': '1.1.1.1'}",
                'var2': "'value2'"
            }
        }
        path = os.path.join(report_dir, 'report.json')
        with open(path) as report_file:
            actual = json.load(report_file)
            assert actual == expected