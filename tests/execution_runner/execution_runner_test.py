import json
import os
from types import SimpleNamespace

import pytest

from golem.execution_runner import execution_runner as exc_runner
from golem.core import test
from golem.core import test_data
from golem.core import environment_manager
from golem.core import utils
from golem.core import settings_manager
from golem.core import file_manager
from golem.core import session
from golem.report import execution_report as exec_report


class TestDefineBrowsers:

    remote_browsers = {
        'chrome_60_mac': {
            'browserName': 'chrome',
            'version': '60.0',
            'platform': 'macOS 10.12'
        }
    }

    default_browsers = ['chrome', 'chrome-headless']

    custom_browsers = []

    def test_define_browsers(self):
        """Verify that _define_browsers returns the correct values"""
        browsers = ['chrome', 'chrome_60_mac']
        expected = [
            {
                'name': 'chrome',
                'full_name': None,
                'remote': False,
                'capabilities': {}
            },
            {
                'name': 'chrome',
                'full_name': 'chrome_60_mac',
                'remote': True,
                'capabilities': {
                    'browserName': 'chrome',
                    'version': '60.0',
                    'platform': 'macOS 10.12'
                }
            }
        ]
        drivers_defined = exc_runner.define_browsers(browsers, self.remote_browsers,
                                                     self.default_browsers, self.custom_browsers)
        assert drivers_defined == expected

    def test_define_browsers_drivers_empty(self):
        """Verify that _define_browsers returns correct value
        when selected drivers is empty
        """
        drivers = []
        expected = []
        drivers_defined = exc_runner.define_browsers(drivers, self.remote_browsers,
                                                     self.default_browsers, self.custom_browsers)
        assert drivers_defined == expected

    def test_define_browsers_driver_is_not_defined(self):
        """Verify that _define_browsers raises the correct exception
        when a driver name that is not defined is passed
        """
        drivers = ['not_defined']
        expected_msg = ['Error: the browser {} is not defined\n'.format('not_defined'),
                        'available options are:\n',
                        '\n'.join(self.default_browsers),
                        '\n'.join(list(self.remote_browsers.keys()))]
        expected_msg = ''.join(expected_msg)
        with pytest.raises(Exception) as excinfo:      
            _ = exc_runner.define_browsers(drivers, self.remote_browsers, self.default_browsers, self.custom_browsers)
        assert str(excinfo.value) == expected_msg

    def test_define_browsers_browser_order_of_preference(self):
        """Verify that _define_browsers selects the drivers in the correct
        order of precedence, first remote drivers then predefined drivers"""
        remote_drivers = {
            'chromex': {
                'browserName': 'chrome',
                'version': '60.0',
                'platform': 'macOS 10.12'
            }
        }
        default_drivers = ['chromex']
        drivers = ['chromex']
        drivers_defined = exc_runner.define_browsers(drivers, remote_drivers, default_drivers, self.custom_browsers)
        assert len(drivers_defined) == 1
        assert drivers_defined[0]['remote'] is True
        assert drivers_defined[0]['capabilities']['version'] == '60.0'


class TestSelectEnvironments:

    @pytest.mark.slow
    def test__select_environments(self, project_session):
        """Verify that _select_environments uses the correct order
        of precedence"""
        _, project = project_session.activate()
        cli_envs = ['cli_env_1', 'cli_env_2']
        execution_runner = exc_runner.ExecutionRunner(project)
        execution_runner.cli_args.envs = cli_envs
        execution_runner.suite.envs = ['suite_env_1', 'suite_env_2']
        project_envs = environment_manager.get_envs(project)
        result_envs = execution_runner._select_environments(project_envs)
        assert result_envs == cli_envs

    @pytest.mark.slow
    def test__select_environments_cli_envs_empty(self, project_function):
        """Verify that _select_environments uses the correct order
        of precedence when cli environments is empty"""
        testdir, project = project_function.activate()
        cli_envs = []
        suite_envs = ['suite_env_1', 'suite_env_2']
        execution_runner = exc_runner.ExecutionRunner(project)
        execution_runner.cli_args.envs = cli_envs
        execution_runner.suite.envs = suite_envs
        path = os.path.join(testdir, 'environments.json')
        with open(path, 'w+') as f:
            f.write('{"env1": {}, "env2": {}}')
        project_envs = environment_manager.get_envs(project)
        result_envs = execution_runner._select_environments(project_envs)
        assert result_envs == suite_envs

    @pytest.mark.slow
    def test__select_environments_cli_envs_empty_suite_envs_empty(self, project_function):
        """Verify that _select_environments uses the correct order
        of precedence when cli environments and suite environments are empty"""
        testdir, project = project_function.activate()
        execution_runner = exc_runner.ExecutionRunner(project)
        execution_runner.cli_args.envs = []
        execution_runner.suite.envs = []
        path = os.path.join(testdir, 'projects', project, 'environments.json')
        with open(path, 'w+') as f:
            f.write('{"env3": {}, "env4": {}}')
        project_envs = environment_manager.get_envs(project)
        result_envs = execution_runner._select_environments(project_envs)
        assert result_envs == ['env3']

    @pytest.mark.slow
    def test__select_environments_all_envs_empty(self, project_function):
        """Verify that _select_environments uses the correct order
        of precedence when cli environments, suite environments and 
        project environments are empty"""
        _, project = project_function.activate()
        execution_runner = exc_runner.ExecutionRunner(project)
        execution_runner.cli_args.envs = []
        execution_runner.cli_args.envs = []
        project_envs = environment_manager.get_envs(project)
        result_envs = execution_runner._select_environments(project_envs)
        assert result_envs == []


class TestDefineExecutionList:

    @pytest.mark.slow
    def test_define_execution_list(self, project_function_clean):
        """Verify that the execution list is generated properly when there's only
        one test without datasets, one driver and zero environments
        """
        _, project = project_function_clean.activate()
        execution_runner = exc_runner.ExecutionRunner(project)
        execution_runner.tests = ['test_001']
        execution_runner.execution.processes = 1
        execution_runner.execution.browsers = ['chrome']
        execution_runner.execution.envs = []
        execution_list = execution_runner._define_execution_list()
        expected_list = [
            SimpleNamespace(name='test_001', data_set={}, secrets={}, browser='chrome',
                            reportdir=None, env=None, set_name='')
        ]
        assert execution_list == expected_list

    @pytest.mark.slow
    def test_define_execution_list_multiple_data_sets(self, project_function_clean):
        """Verify that the execution list is generated properly when a test
        has multiple data sets
        """
        _, project = project_function_clean.activate()
        test_name = 'test_002'
        test.create_test(project, test_name)
        tdata = [
            {
                'col1': 'a',
                'col2': 'b'
            },
            {
                'col1': 'c',
                'col2': 'd',
            }

        ]
        test_data.save_external_test_data_file(project, test_name, tdata)
        execution_runner = exc_runner.ExecutionRunner(project)
        execution_runner.tests = [test_name]
        execution_runner.execution.processes = 1
        execution_runner.execution.browsers = ['chrome']
        execution_runner.execution.envs = []
        execution_list = execution_runner._define_execution_list()
        assert execution_list[0].data_set == {'col1': 'a', 'col2': 'b'}
        assert isinstance(execution_list[0].set_name, str) and execution_list[0].set_name != ''
        assert execution_list[1].data_set == {'col1': 'c', 'col2': 'd'}
        assert isinstance(execution_list[1].set_name, str) and execution_list[1].set_name != ''

    @pytest.mark.slow
    def test_define_execution_list_multiple_tests(self, project_function_clean):
        """Verify that the execution list is generated properly when there
        are multiple tests in the list
        """
        _, project = project_function_clean.activate()
        # create test one
        test_name_one = 'test_one_001'
        test.create_test(project, test_name_one)
        tdata = [
            {
                'col1': 'a',
                'col2': 'b'
            },
            {
                'col1': 'c',
                'col2': 'd',
            }
        ]
        test_data.save_external_test_data_file(project, test_name_one, tdata)
        # create test two
        test_name_two = 'test_two_001'
        test.create_test(project, test_name_two)
        execution_runner = exc_runner.ExecutionRunner(project)
        execution_runner.tests = [test_name_one, test_name_two]
        execution_runner.execution.processes = 1
        execution_runner.execution.browsers = ['chrome']
        execution_runner.execution.envs = []
        exec_list = execution_runner._define_execution_list()
        assert exec_list[0].name == 'test_one_001'
        assert exec_list[0].data_set == {'col1': 'a', 'col2': 'b'}
        assert exec_list[1].name == 'test_one_001'
        assert exec_list[1].data_set == {'col1': 'c', 'col2': 'd'}
        assert exec_list[2].name == 'test_two_001'
        assert exec_list[2].data_set == {}

    @pytest.mark.slow
    def test_define_execution_list_multiple_envs(self, project_function_clean):
        """Verify that the execution list is generated properly when the execution
        has multiple envs
        """
        _, project = project_function_clean.activate()
        # create test one
        test_name_one = 'test_one_003'
        test.create_test(project, test_name_one)
        # create two environments in environments.json
        env_data = {
            "stage": {"url": "xxx"},
            "preview": {"url": "yyy"}
        }
        env_data_json = json.dumps(env_data)
        environment_manager.save_environments(project, env_data_json)
        execution_runner = exc_runner.ExecutionRunner(project)
        execution_runner.tests = [test_name_one]
        execution_runner.execution.processes = 1
        execution_runner.execution.browsers = ['chrome']
        execution_runner.execution.envs = ['stage', 'preview']
        exec_list = execution_runner._define_execution_list()
        assert exec_list[0].data_set == {'env': {'url': 'xxx', 'name': 'stage'}}
        assert exec_list[0].env == 'stage'
        assert exec_list[1].data_set == {'env': {'url': 'yyy', 'name': 'preview'}}
        assert exec_list[1].env == 'preview'

    @pytest.mark.slow
    def test_define_execution_list_multiple_drivers(self, project_function_clean):
        """Verify that the execution list is generated properly when there
        are multiple drivers in the list
        """
        _, project = project_function_clean.activate()
        # create test one
        test_name_one = 'test_one_004'
        test.create_test(project, test_name_one)
        # create test two
        test_name_two = 'test_two_004'
        test.create_test(project, test_name_two)
        execution_runner = exc_runner.ExecutionRunner(project)
        execution_runner.tests = [test_name_one, test_name_two]
        execution_runner.execution.processes = 1
        execution_runner.execution.browsers = ['chrome', 'firefox']
        execution_runner.execution.envs = []
        execution_list = execution_runner._define_execution_list()
        # expected_list = [
        #     SimpleNamespace(name='test_one_004', data_set={}, secrets={}, browser='chrome', reportdir=None, env=None, set_name=''),
        #     SimpleNamespace(name='test_one_004', data_set={}, secrets={}, browser='firefox', reportdir=None, env=None, set_name=''),
        #     SimpleNamespace(name='test_two_004', data_set={}, secrets={}, browser='chrome', reportdir=None, env=None, set_name=''),
        #     SimpleNamespace(name='test_two_004', data_set={}, secrets={}, browser='firefox', reportdir=None, env=None, set_name='')
        # ]
        # assert execution_list == expected_list
        assert len(execution_list) == 4
        assert execution_list[0].browser == 'chrome'
        assert execution_list[1].browser == 'firefox'
        assert execution_list[2].browser == 'chrome'
        assert execution_list[3].browser == 'firefox'

    @pytest.mark.slow
    def test_define_execution_list_multiple_tests_datasets_drivers_envs(
            self, project_function_clean):
        """Verify that the execution list is generated properly when there
        are multiple tests, data sets, drivers and environments
        """
        _, project = project_function_clean.activate()
        # create test one
        test_name_one = 'test_one_005'
        test.create_test(project, test_name_one)
        # test data for test one
        tdata = [
            {'col1': 'a'},
            {'col1': 'b'}
        ]
        test_data.save_external_test_data_file(project, test_name_one, tdata)
        # create test two
        test_name_two = 'test_two_005'
        test.create_test(project, test_name_two)
        # create two environments
        env_data = {
            "stage": {"url": "xxx"},
            "preview": {"url": "yyy"}
        }
        env_data_json = json.dumps(env_data)
        environment_manager.save_environments(project, env_data_json)
        execution_runner = exc_runner.ExecutionRunner(project)
        execution_runner.tests = [test_name_one, test_name_two]
        execution_runner.execution.processes = 1
        execution_runner.execution.browsers = ['chrome', 'firefox']
        execution_runner.execution.envs = ['stage', 'preview']
        ex = execution_runner._define_execution_list()
        assert ex[0].browser == 'chrome' and ex[0].env == 'stage' and \
               ex[0].data_set == {'col1': 'a', 'env': {'url': 'xxx', 'name': 'stage'}}
        assert ex[1].browser == 'firefox' and ex[1].env == 'stage' and \
               ex[1].data_set == {'col1': 'a', 'env': {'url': 'xxx', 'name': 'stage'}}
        assert ex[2].browser == 'chrome' and ex[2].env == 'preview' and \
               ex[2].data_set == {'col1': 'a', 'env': {'url': 'yyy', 'name': 'preview'}}
        assert ex[3].browser == 'firefox' and ex[3].env == 'preview' and \
               ex[3].data_set == {'col1': 'a', 'env': {'url': 'yyy', 'name': 'preview'}}
        assert ex[4].browser == 'chrome' and ex[4].env == 'stage' and \
               ex[4].data_set == {'col1': 'b', 'env': {'url': 'xxx', 'name': 'stage'}}
        assert ex[5].browser == 'firefox' and ex[5].env == 'stage' and \
               ex[5].data_set == {'col1': 'b', 'env': {'url': 'xxx', 'name': 'stage'}}
        assert ex[6].browser == 'chrome' and ex[6].env == 'preview' and \
               ex[6].data_set == {'col1': 'b', 'env': {'url': 'yyy', 'name': 'preview'}}
        assert ex[7].browser == 'firefox' and ex[7].env == 'preview' and \
               ex[7].data_set == {'col1': 'b', 'env': {'url': 'yyy', 'name': 'preview'}}
        assert ex[8].browser == 'chrome' and ex[8].env == 'stage' and \
               ex[8].data_set == {'env': {'url': 'xxx', 'name': 'stage'}}
        assert ex[9].browser == 'firefox' and ex[9].env == 'stage' and \
               ex[9].data_set == {'env': {'url': 'xxx', 'name': 'stage'}}
        assert ex[10].browser == 'chrome' and ex[10].env == 'preview' and \
               ex[10].data_set == {'env': {'url': 'yyy', 'name': 'preview'}}
        assert ex[11].browser == 'firefox' and ex[11].env == 'preview' and \
               ex[11].data_set == {'env': {'url': 'yyy', 'name': 'preview'}}

    @pytest.mark.slow
    def test_define_execution_list_with_secrets(self, project_function_clean):
        """Verify that the execution list is generated properly when there's only
        one test without datasets, one driver and zero environments
        """
        _, project = project_function_clean.activate()
        secrets = {"a": "secret", "b": "secret02"}
        secrets_path = os.path.join(project_function_clean.path, 'secrets.json')
        with open(secrets_path, 'w') as secrets_file:
            secrets_file.write(json.dumps(secrets, indent=True))
        execution_runner = exc_runner.ExecutionRunner(project)
        execution_runner.tests = ['test_001']
        execution_runner.execution.processes = 1
        execution_runner.execution.browsers = ['chrome']
        execution_runner.execution.envs = []
        execution_list = execution_runner._define_execution_list()
        expected_list = [
            SimpleNamespace(name='test_001', data_set={}, secrets={"a": "secret", "b": "secret02"}, browser='chrome', reportdir=None, env=None, set_name='')
        ]
        assert execution_list == expected_list


class TestRunSingleTest:

    @pytest.mark.slow
    def test_run_single_test(self, project_class, test_utils):
        testdir, project = project_class.activate()
        test_name = 'foo001'
        timestamp = utils.get_timestamp()
        session.settings = settings_manager.get_project_settings(project)
        test_utils.create_test(project, test_name)
        execution_runner = exc_runner.ExecutionRunner(project, browsers=['chrome'], timestamp=timestamp)
        execution_runner.run_test(test_name)
        test_report_dir = os.path.join(testdir, 'projects', project, 'reports', test_name, timestamp)
        assert os.path.isdir(test_report_dir)
        items = os.listdir(test_report_dir)
        # test set dir + report.json
        assert len(items) == 2

    @pytest.mark.slow
    def test_run_single_test_with_two_sets(self, project_class, test_utils, capsys):
        """Run a single test with two data sets.
        It should display the number of tests and test sets found."""
        testdir, project = project_class.activate()
        test_name = 'foo002'
        timestamp = utils.get_timestamp()
        session.settings = settings_manager.get_project_settings(project)
        content = ('data = [{"foo": 1}, {"foo": 2}]\n'
                   'def test(data):\n'
                   '    pass\n')
        test_utils.create_test(project, test_name, content=content)
        execution_runner = exc_runner.ExecutionRunner(project, browsers=['chrome'], timestamp=timestamp)
        execution_runner.run_test(test_name)
        out, err = capsys.readouterr()
        # number of tests is displayed
        assert 'Tests found: 1 (2 sets)' in out
        test_report_dir = os.path.join(testdir, 'projects', project, 'reports', test_name, timestamp)
        assert os.path.isdir(test_report_dir)
        items = os.listdir(test_report_dir)
        # two test set dirs + report.json
        assert len(items) == 3

    @pytest.mark.slow
    def test_run_single_test_filter_by_tags(self, project_class, test_utils):
        """Run a single test with filtering by tags"""
        testdir, project = project_class.activate()
        test_name = 'foo003'
        timestamp = utils.get_timestamp()
        session.settings = settings_manager.get_project_settings(project)
        content = ('tags = ["alfa", "bravo"]\n'
                   'def test(data):\n'
                   '    pass\n')
        test_utils.create_test(project, test_name, content=content)
        execution_runner = exc_runner.ExecutionRunner(project, browsers=['chrome'], timestamp=timestamp,
                                                      tags=['alfa'])
        execution_runner.run_test(test_name)
        test_report_dir = os.path.join(testdir, 'projects', project, 'reports', test_name, timestamp)
        assert os.path.isdir(test_report_dir)
        items = os.listdir(test_report_dir)
        # test set dir + report.json
        assert len(items) == 2

    @pytest.mark.slow
    def test_run_single_test_with_invalid_tags(self, project_class, test_utils, capsys):
        testdir, project = project_class.activate()
        test_name = 'foo004'
        timestamp = utils.get_timestamp()
        content = ('tags = ["alfa", "bravo"]\n'
                   'def test(data):\n'
                   '    pass\n')
        test_utils.create_test(project, test_name, content=content)
        execution_runner = exc_runner.ExecutionRunner(project, browsers=['chrome'], timestamp=timestamp,
                                                      tags=['charlie'])
        execution_runner.run_test(test_name)
        out, err = capsys.readouterr()
        assert 'No tests found with tag(s): charlie' in out
        test_report_dir = os.path.join(testdir, 'projects', project, 'reports', test_name, timestamp)
        assert os.path.isdir(test_report_dir)
        items = os.listdir(test_report_dir)
        # only report.json is present
        assert items == ['report.json']


class TestRunSuite:

    @pytest.fixture(scope="class")
    def _project_with_tags(self, project_class, test_utils):
        """A fixture of a project with tests that contain tags"""
        _, project = project_class.activate()
        tests = SimpleNamespace()
        base_content = 'def test(data):\n     pass\n'
        tests.test_alfa_bravo = 'test_alfa_bravo'
        content = 'tags = ["alfa", "bravo"]'
        test_utils.create_test(project, tests.test_alfa_bravo, content=base_content+content)
        tests.test_bravo_charlie = 'test_bravo_charlie'
        content = 'tags = ["bravo", "charlie"]'
        test_utils.create_test(project, tests.test_bravo_charlie, content=base_content+content)
        tests.test_empty_tags = 'test_empty_tags'
        content = 'tags = []'
        test_utils.create_test(project, tests.test_empty_tags, content=base_content+content)
        tests.test_no_tags = 'test_no_tags'
        content = 'def test(data):\n     pass'
        test_utils.create_test(project, tests.test_no_tags, content=base_content+content)
        project_class.tests = list(tests.__dict__)
        project_class.t = tests
        return project_class

    @pytest.mark.slow
    def test_run_suite(self, _project_with_tags, test_utils, capsys):
        _, project = _project_with_tags.activate()
        suite_name = test_utils.random_numeric_string(10, 'suite')
        tests = [_project_with_tags.t.test_alfa_bravo,
                 _project_with_tags.t.test_bravo_charlie]
        test_utils.create_suite(project, suite_name, tests=tests)
        timestamp = utils.get_timestamp()
        execution_runner = exc_runner.ExecutionRunner(project, browsers=['chrome'], timestamp=timestamp)
        execution_runner.run_suite(suite_name)
        out, err = capsys.readouterr()
        assert 'Tests found: 2' in out
        data = exec_report.get_execution_data(project=project, execution=suite_name, timestamp=timestamp)
        assert data['has_finished'] is True
        assert data['total_tests'] == 2

    def test_run_suite_without_tests(self, _project_with_tags, test_utils, capsys):
        _, project = _project_with_tags.activate()
        suite_name = test_utils.random_numeric_string(10, 'suite')
        test_utils.create_suite(project, suite_name, tests=[])
        timestamp = utils.get_timestamp()
        execution_runner = exc_runner.ExecutionRunner(project, browsers=['chrome'], timestamp=timestamp)
        execution_runner.run_suite(suite_name)
        out, err = capsys.readouterr()
        assert 'No tests found for suite {}'.format(suite_name) in out
        data = exec_report.get_execution_data(project=project, execution=suite_name, timestamp=timestamp)
        assert data['has_finished'] is True
        assert data['total_tests'] == 0

    @pytest.mark.slow
    def test_run_suite_filter_by_tags(self, _project_with_tags, test_utils, capsys):
        _, project = _project_with_tags.activate()
        suite_name = test_utils.random_numeric_string(10, 'suite')
        tests = [_project_with_tags.t.test_alfa_bravo,
                 _project_with_tags.t.test_bravo_charlie]
        test_utils.create_suite(project, suite_name, tests=tests)
        timestamp = utils.get_timestamp()
        execution_runner = exc_runner.ExecutionRunner(project, browsers=['chrome'],
                                                      timestamp=timestamp,
                                                      tags=['alfa', 'bravo'])
        execution_runner.run_suite(suite_name)
        out, err = capsys.readouterr()
        assert 'Tests found: 1' in out
        data = exec_report.get_execution_data(project=project, execution=suite_name, timestamp=timestamp)
        assert data['has_finished'] is True
        assert data['total_tests'] == 1

    @pytest.mark.slow
    def test_run_suite_filter_by_invalid_tags(self, _project_with_tags, test_utils, capsys):
        _, project = _project_with_tags.activate()
        suite_name = test_utils.random_numeric_string(10, 'suite')
        tests = [_project_with_tags.t.test_alfa_bravo,
                 _project_with_tags.t.test_bravo_charlie]
        test_utils.create_suite(project, suite_name, tests=tests)
        timestamp = utils.get_timestamp()
        execution_runner = exc_runner.ExecutionRunner(project, browsers=['chrome'],
                                                      timestamp=timestamp,
                                                      tags=['sierra', 'tango'])
        execution_runner.run_suite(suite_name)
        out, err = capsys.readouterr()
        assert 'No tests found with tag(s): sierra, tango' in out
        data = exec_report.get_execution_data(project=project, execution=suite_name, timestamp=timestamp)
        assert data['has_finished'] is True
        assert data['total_tests'] == 0

    def test_run_suite_filter_by_invalid_tag_expression(self, _project_with_tags,
                                                        test_utils, capsys):
        """When a invalid tag expression is used a message is displayed
        to the console, no tests are run, the report is generated,
        and the execution exists with status code 1
        """
        _, project = _project_with_tags.activate()
        suite_name = test_utils.random_numeric_string(10, 'suite')
        tests = [_project_with_tags.t.test_alfa_bravo,
                 _project_with_tags.t.test_bravo_charlie]
        test_utils.create_suite(project, suite_name, tests=tests)
        timestamp = utils.get_timestamp()
        execution_runner = exc_runner.ExecutionRunner(project, browsers=['chrome'],
                                                      timestamp=timestamp,
                                                      tags=['sierra = tango'])
        with pytest.raises(SystemExit):
            execution_runner.run_suite(suite_name)
        out, err = capsys.readouterr()
        expected = ("InvalidTagExpression: unknown expression <class '_ast.Assign'>, the "
                    "only valid operators for tag expressions are: 'and', 'or' & 'not'")
        # TODO: py 3.9
        expected2 = ("InvalidTagExpression: unknown expression <class 'ast.Assign'>, the "
                    "only valid operators for tag expressions are: 'and', 'or' & 'not'")
        assert expected in out or expected2 in out
        data = exec_report.get_execution_data(project=project, execution=suite_name, timestamp=timestamp)
        assert data['has_finished'] is True
        assert data['total_tests'] == 0


class TestRunDirectory:

    @pytest.fixture(scope="class")
    def _project_with_tags(self, project_class, test_utils):
        """A fixture of a project with tests that contain tags"""
        testdir, project = project_class.activate()
        tests = SimpleNamespace()
        base_content = 'def test(data):\n     pass\n'
        tests.test_alfa_bravo = 'test_alfa_bravo'
        content = 'tags = ["alfa", "bravo"]'
        test_name = '{}.{}'.format('foo', tests.test_alfa_bravo)
        test_utils.create_test(project, test_name, content=base_content + content)
        tests.test_bravo_charlie = 'test_bravo_charlie'
        content = 'tags = ["bravo", "charlie"]'
        test_name = '{}.{}'.format('foo', tests.test_bravo_charlie)
        test_utils.create_test(project, test_name, content=base_content + content)
        tests.test_empty_tags = 'test_empty_tags'
        content = 'tags = []'
        test_utils.create_test(project, tests.test_empty_tags, content=base_content + content)
        tests.test_no_tags = 'test_no_tags'
        content = 'def test(data):\n     pass'
        test_utils.create_test(project, tests.test_no_tags, content=base_content + content)
        path_list = [testdir, 'projects', project, 'tests', 'empty']
        file_manager.create_directory(path_list=path_list, add_init=True)
        project_class.tests = list(tests.__dict__)
        project_class.t = tests
        return project_class

    @pytest.mark.slow
    def test_run_directory(self, _project_with_tags, capsys):
        _, project = _project_with_tags.activate()
        timestamp = utils.get_timestamp()
        execution_runner = exc_runner.ExecutionRunner(project, browsers=['chrome'],
                                                      timestamp=timestamp)
        execution_runner.run_directory('foo')
        out, err = capsys.readouterr()
        assert 'Tests found: 2' in out
        data = exec_report.get_execution_data(project=project, execution='foo', timestamp=timestamp)
        assert data['has_finished'] is True
        assert data['total_tests'] == 2

    def test_run_directory_without_tests(self, _project_with_tags, capsys):
        _, project = _project_with_tags.activate()
        timestamp = utils.get_timestamp()
        dirname = 'empty'
        execution_runner = exc_runner.ExecutionRunner(project, browsers=['chrome'], timestamp=timestamp)
        execution_runner.run_directory(dirname)
        out, err = capsys.readouterr()
        expected = 'No tests were found in {}'.format(os.path.join('tests', dirname))
        assert expected in out
        data = exec_report.get_execution_data(project=project, execution=dirname, timestamp=timestamp)
        assert data['has_finished'] is True
        assert data['total_tests'] == 0

    @pytest.mark.slow
    def test_run_directory_filter_by_tags(self, _project_with_tags, test_utils, capsys):
        _, project = _project_with_tags.activate()
        timestamp = utils.get_timestamp()
        dirname = 'foo'
        execution_runner = exc_runner.ExecutionRunner(project, browsers=['chrome'],
                                                      timestamp=timestamp,
                                                      tags=['alfa', 'bravo'])
        execution_runner.run_directory(dirname)
        out, err = capsys.readouterr()
        assert 'Tests found: 1' in out
        data = exec_report.get_execution_data(project=project, execution=dirname, timestamp=timestamp)
        assert data['has_finished'] is True
        assert data['total_tests'] == 1


class TestRunWithEnvs:

    @pytest.mark.slow
    def test_run_with_environments(self, project_function, test_utils, capsys):
        _, project = project_function.activate()
        environments = json.dumps({'test': {}, 'stage': {}})
        environment_manager.save_environments(project, environments)
        test_utils.create_test(project, 'test01')
        timestamp = utils.get_timestamp()
        execution_runner = exc_runner.ExecutionRunner(project, browsers=['chrome'],
                                                      timestamp=timestamp,
                                                      environments=['test', 'stage'])
        execution_runner.run_directory('')
        out, err = capsys.readouterr()
        assert 'Tests found: 1 (2 sets)' in out
        data = exec_report.get_execution_data(project=project, execution='all', timestamp=timestamp)
        assert data['has_finished'] is True
        assert data['total_tests'] == 2

    def test_run_with_not_existing_environments(self, project_function, test_utils, capsys):
        """Run tests with a not existing environment.
        It should throw an error and finish with status code 1
        """
        _, project = project_function.activate()
        test_utils.create_test(project, 'test01')
        timestamp = utils.get_timestamp()
        execution_runner = exc_runner.ExecutionRunner(project, browsers=['chrome'],
                                                      timestamp=timestamp,
                                                      environments=['not_existing'])
        with pytest.raises(SystemExit) as wrapped_execution:
            execution_runner.run_directory('')

        assert wrapped_execution.value.code == 1
        out, err = capsys.readouterr()
        msg = ('ERROR: the following environments do not exist for project {}: '
               'not_existing'.format(project))
        assert msg in out
        data = exec_report.get_execution_data(project=project, execution='all', timestamp=timestamp)
        assert data['has_finished'] is True
        assert data['total_tests'] == 0
