import json
import os

import pytest

from golem.test_runner import start_execution
from golem.core import test_case, test_data, environment_manager, utils

from tests.fixtures import testdir_fixture
from tests.helper_functions import create_random_project


class Test__define_drivers:
    """Tests for golem.test_runner.start_execution._define_drivers()"""

    remote_drivers = {
        'chrome_60_mac': {
            'browserName': 'chrome',
            'version': '60.0',
            'platform': 'macOS 10.12'
        }
    }

    default_drivers = ['chrome', 'chrome-headless']

    def test__define_drivers(self):
        """Verify that _define_drivers returns the correct values"""

        drivers = ['chrome', 'chrome_60_mac']
        
        expected = [
            {
                'name': 'chrome',
                'full_name': None,
                'remote': False,
                'capabilities': None
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

        drivers_defined = start_execution._define_drivers(drivers, self.remote_drivers,
                                                          self.default_drivers)
        assert drivers_defined == expected


    def test__define_drivers_drivers_empty(self):
        """Verify that _define_drivers returns correct value 
        when selected drivers is empty
        """
        drivers = []
        expected = []

        drivers_defined = start_execution._define_drivers(drivers, self.remote_drivers,
                                                          self.default_drivers)
        assert drivers_defined == expected


    def test__define_drivers_driver_is_not_defined(self):
        """Verify that _define_drivers raises the correct exception
        when a driver name that is not defined is passed
        """
        drivers = ['not_defined']

        expected_msg = ['Error: the browser {} is not defined\n'.format('not_defined'),
                        'available options are:\n',
                        '\n'.join(self.default_drivers),
                        '\n'.join(list(self.remote_drivers.keys()))]
        expected_msg = ''.join(expected_msg)

        with pytest.raises(Exception) as excinfo:      
            drivers_defined = start_execution._define_drivers(drivers,
                                                              self.remote_drivers,
                                                              self.default_drivers)
        assert str(excinfo.value) == expected_msg


    def test__define_drivers_driver_order_of_preference(self):
        """Verify that _define_drivers selects the drivers in the correct
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
   
        drivers_defined = start_execution._define_drivers(drivers,
                                                          remote_drivers,
                                                          default_drivers)
        assert len(drivers_defined) == 1
        assert drivers_defined[0]['remote'] == True
        assert drivers_defined[0]['capabilities']['version'] == '60.0'


class Test__select_environments:
    """Tests for golem.test_runner.start_execution._select_environments()"""

    def test__select_environments(self):
        """Verify that _select_environments uses the correct order
        of precedence"""
        cli_envs = ['cli_env_1', 'cli_env_2']
        suite_envs = ['suite_env_1', 'suite_env_2']
        project_envs = ['proj_env_1', 'proj_env_2']
        result_envs = start_execution._select_environments(cli_envs, suite_envs, project_envs)
        assert result_envs == cli_envs


    def test__select_environments_cli_envs_empty(self):
        """Verify that _select_environments uses the correct order
        of precedence when cli environments is empty"""
        cli_envs = []
        suite_envs = ['suite_env_1', 'suite_env_2']
        project_envs = ['proj_env_1', 'proj_env_2']
        result_envs = start_execution._select_environments(cli_envs, suite_envs, project_envs)
        assert result_envs == suite_envs


    def test__select_environments_cli_envs_empty_suite_envs_empty(self):
        """Verify that _select_environments uses the correct order
        of precedence when cli environments and suite environments are empty"""
        cli_envs = []
        suite_envs = []
        project_envs = ['proj_env_1', 'proj_env_2']
        result_envs = start_execution._select_environments(cli_envs, suite_envs, project_envs)
        assert result_envs == [project_envs[0]]


    def test__select_environments_all_envs_empty(self):
        """Verify that _select_environments uses the correct order
        of precedence when cli environments, suite environments and 
        project environments are empty"""
        cli_envs = []
        suite_envs = []
        project_envs = []
        result_envs = start_execution._select_environments(cli_envs, suite_envs, project_envs)
        assert result_envs == ['']


class Test__define_execution_list:
    """Tests for golem.test_runner.start_execution._define_execution_list()"""

    def test_define_execution_list(self, testdir_fixture):
        """Verify that the execution list is generated properly when there's only
        one test without datasets, one driver and zero environments
        """
        root_path = testdir_fixture['path']
        project = create_random_project(root_path)
        test_name = 'new_test_case_001'
        parents = []
        test_case.new_test_case(root_path, project, parents, test_name)

        execution = {
            'tests': [test_name],
            'workers': 1,
            'drivers': ['chrome'],
            'environments': [''],
            'suite_before': None,
            'suite_after': None
        }

        execution_list = start_execution._define_execution_list(root_path, project, execution)
        
        expected_list = [
            {
                'test_name': 'new_test_case_001',
                'data_set': {},
                'driver': 'chrome',
                'report_directory': None
            }
        ]
        assert execution_list == expected_list


    def test_define_execution_list_multiple_data_sets(self, testdir_fixture):
        """Verify that the execution list is generated properly when a test
        has multiple data sets
        """
        root_path = testdir_fixture['path']
        project = create_random_project(root_path)
        test_name = 'new_test_case_002'
        parents = []
        test_case.new_test_case(root_path, project, parents, test_name)

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
        test_data.save_external_test_data_file(root_path, project, test_name, tdata)

        execution = {
            'tests': [test_name],
            'workers': 1,
            'drivers': ['chrome'],
            'environments': [''],
            'suite_before': None,
            'suite_after': None
        }

        execution_list = start_execution._define_execution_list(root_path, project,
                                                                execution)
        
        expected_list = [
            {
                'test_name': 'new_test_case_002',
                'data_set': {'col1': 'a', 'col2': 'b'},
                'driver': 'chrome',
                'report_directory': None
            },
            {
                'test_name': 'new_test_case_002',
                'data_set': {'col1': 'c', 'col2': 'd'},
                'driver': 'chrome',
                'report_directory': None
            }
        ]
        assert execution_list == expected_list


    def test_define_execution_list_multiple_tests(self, testdir_fixture):
        """Verify that the execution list is generated properly when there
        are multiple tests in the list
        """
        root_path = testdir_fixture['path']
        project = create_random_project(root_path)
        # create test one
        test_name_one = 'new_test_case_one'
        parents = []
        test_case.new_test_case(root_path, project, parents, test_name_one)
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
        test_data.save_external_test_data_file(root_path, project, test_name_one, tdata)

        # create test two
        test_name_two = 'new_test_case_two'
        parents = []
        test_case.new_test_case(root_path, project, parents, test_name_two)

        execution = {
            'tests': [test_name_one, test_name_two],
            'workers': 1,
            'drivers': ['chrome'],
            'environments': [''],
            'suite_before': None,
            'suite_after': None
        }

        execution_list = start_execution._define_execution_list(root_path, project,
                                                                execution)
        
        expected_list = [
            {
                'test_name': 'new_test_case_one',
                'data_set': {'col1': 'a', 'col2': 'b'},
                'driver': 'chrome',
                'report_directory': None
            },
            {
                'test_name': 'new_test_case_one',
                'data_set': {'col1': 'c', 'col2': 'd'},
                'driver': 'chrome',
                'report_directory': None
            },
            {
                'test_name': 'new_test_case_two',
                'data_set': {},
                'driver': 'chrome',
                'report_directory': None
            }
        ]
        assert execution_list == expected_list


    def test_define_execution_list_multiple_envs(self, testdir_fixture):
        """Verify that the execution list is generated properly when the execution
        has multiple envs
        """
        root_path = testdir_fixture['path']
        project = create_random_project(root_path)
        # create test one
        test_name_one = 'new_test_case_one'
        parents = []
        test_case.new_test_case(root_path, project, parents, test_name_one)

        # create two environments in environments.json
        env_data = {
            "stage": {
                "url": "xxx"
            },
            "preview": {
                "url": "yyy"
            }
        }
        env_data_json = json.dumps(env_data)
        environment_manager.save_environments(root_path, project, env_data_json)

        execution = {
            'tests': [test_name_one],
            'workers': 1,
            'drivers': ['chrome'],
            'environments': ['stage', 'preview'],
            'suite_before': None,
            'suite_after': None
        }

        execution_list = start_execution._define_execution_list(root_path, project,
                                                                execution)
        
        expected_list = [
            {
                'test_name': 'new_test_case_one',
                'data_set': {'env': {'url': 'xxx', 'name': 'stage'}},
                'driver': 'chrome',
                'report_directory': None
            },
            {
                'test_name': 'new_test_case_one',
                'data_set': {'env': {'url': 'yyy', 'name': 'preview'}},
                'driver': 'chrome',
                'report_directory': None
            },
        ]
        assert execution_list == expected_list


    def test_define_execution_list_multiple_drivers(self, testdir_fixture):
        """Verify that the execution list is generated properly when there
        are multiple drivers in the list
        """
        root_path = testdir_fixture['path']
        project = create_random_project(root_path)
        # create test one
        test_name_one = 'new_test_case_one'
        parents = []
        test_case.new_test_case(root_path, project, parents, test_name_one)
        # create test two
        test_name_two = 'new_test_case_two'
        parents = []
        test_case.new_test_case(root_path, project, parents, test_name_two)

        execution = {
            'tests': [test_name_one, test_name_two],
            'workers': 1,
            'drivers': ['chrome', 'firefox'],
            'environments': [''],
            'suite_before': None,
            'suite_after': None
        }

        execution_list = start_execution._define_execution_list(root_path, project,
                                                                execution)
        
        expected_list = [
            {
                'test_name': 'new_test_case_one',
                'data_set': {},
                'driver': 'chrome',
                'report_directory': None
            },
            {
                'test_name': 'new_test_case_one',
                'data_set': {},
                'driver': 'firefox',
                'report_directory': None
            },
            {
                'test_name': 'new_test_case_two',
                'data_set': {},
                'driver': 'chrome',
                'report_directory': None
            },
            {
                'test_name': 'new_test_case_two',
                'data_set': {},
                'driver': 'firefox',
                'report_directory': None
            }
        ]
        assert execution_list == expected_list


    def test_define_execution_list_multiple_tests_datasets_drivers_envs(self, testdir_fixture):
        """Verify that the execution list is generated properly when there
        are multiple tests, data sets, drivers and environments
        """
        root_path = testdir_fixture['path']
        project = create_random_project(root_path)
        # create test one
        test_name_one = 'new_test_case_one'
        parents = []
        test_case.new_test_case(root_path, project, parents, test_name_one)
        # test data for test one
        tdata = [
            {
                'col1': 'a',
            },
            {
                'col1': 'b',
            }

        ]
        test_data.save_external_test_data_file(root_path, project, test_name_one, tdata)
        # create test two
        test_name_two = 'new_test_case_two'
        parents = []
        test_case.new_test_case(root_path, project, parents, test_name_two)

        # create two environments
        env_data = {
            "stage": {
                "url": "xxx"
            },
            "preview": {
                "url": "yyy"
            }
        }
        env_data_json = json.dumps(env_data)
        environment_manager.save_environments(root_path, project, env_data_json)
        
        execution = {
            'tests': [test_name_one, test_name_two],
            'workers': 1,
            'drivers': ['chrome', 'firefox'],
            'environments': ['stage', 'preview'],
            'suite_before': None,
            'suite_after': None
        }

        execution_list = start_execution._define_execution_list(root_path, project,
                                                                execution)
        expected_list = [
        {'test_name': 'new_test_case_one', 'data_set': {'col1': 'a', 'env': {'url': 'xxx', 'name': 'stage'}}, 'driver': 'chrome', 'report_directory': None},
        {'test_name': 'new_test_case_one', 'data_set': {'col1': 'a', 'env': {'url': 'xxx', 'name': 'stage'}}, 'driver': 'firefox', 'report_directory': None},
        {'test_name': 'new_test_case_one', 'data_set': {'col1': 'a', 'env': {'url': 'yyy', 'name': 'preview'}}, 'driver': 'chrome', 'report_directory': None},
        {'test_name': 'new_test_case_one', 'data_set': {'col1': 'a', 'env': {'url': 'yyy', 'name': 'preview'}}, 'driver': 'firefox', 'report_directory': None},
        {'test_name': 'new_test_case_one', 'data_set': {'col1': 'b', 'env': {'url': 'xxx', 'name': 'stage'}}, 'driver': 'chrome', 'report_directory': None},
        {'test_name': 'new_test_case_one', 'data_set': {'col1': 'b', 'env': {'url': 'xxx', 'name': 'stage'}}, 'driver': 'firefox', 'report_directory': None},
        {'test_name': 'new_test_case_one', 'data_set': {'col1': 'b', 'env': {'url': 'yyy', 'name': 'preview'}}, 'driver': 'chrome', 'report_directory': None},
        {'test_name': 'new_test_case_one', 'data_set': {'col1': 'b', 'env': {'url': 'yyy', 'name': 'preview'}}, 'driver': 'firefox', 'report_directory': None},
        {'test_name': 'new_test_case_two', 'data_set': {'env': {'url': 'xxx', 'name': 'stage'}}, 'driver': 'chrome', 'report_directory': None},
        {'test_name': 'new_test_case_two', 'data_set': {'env': {'url': 'xxx', 'name': 'stage'}}, 'driver': 'firefox', 'report_directory': None},
        {'test_name': 'new_test_case_two', 'data_set': {'env': {'url': 'yyy', 'name': 'preview'}}, 'driver': 'chrome', 'report_directory': None},
        {'test_name': 'new_test_case_two', 'data_set': {'env': {'url': 'yyy', 'name': 'preview'}}, 'driver': 'firefox', 'report_directory': None}]

        assert execution_list == expected_list


class Test__create_execution_directory:
    """Tests for golem.test_runner.start_execution._create_execution_directory()"""

    def test__create_execution_directory_is_suite(self, testdir_fixture):
        """Verify that create_execution_directory works as expected when 
        a suite is passed on
        """
        root_path = testdir_fixture['path']
        project = create_random_project(root_path)
        timestamp = utils.get_timestamp()
        test_name = 'any_test_name_does_not_matter'
        suite_name = 'any_suite_name'
        is_suite = True

        start_execution._create_execution_directory(root_path, project,
                                                    timestamp, test_name,
                                                    suite_name, is_suite)

        expected_path = os.path.join(root_path, 'projects', project,
                                     'reports', suite_name, timestamp)
        path_exists = os.path.isdir(expected_path)
        assert path_exists


    def test__create_execution_directory_is_suite(self, testdir_fixture):
        """Verify that create_execution_directory works as expected when 
        a not suite is passed on
        """
        root_path = testdir_fixture['path']
        project = create_random_project(root_path)
        timestamp = utils.get_timestamp()
        test_name = 'any_test_name_does_not_matter_2'
        suite_name = 'single_tests'
        is_suite = False

        start_execution._create_execution_directory(root_path, project,
                                                    timestamp, test_name,
                                                    suite_name, is_suite)

        expected_path = os.path.join(root_path, 'projects', project,
                                     'reports', 'single_tests', test_name, timestamp)
        path_exists = os.path.isdir(expected_path)
        assert path_exists
