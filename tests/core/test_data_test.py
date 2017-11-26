from golem.core import utils, test_data, test_case, settings_manager, test_execution

from tests.fixtures import project_fixture, testdir_fixture


class Test_get_test_data:

    def test_get_test_data(self, testdir_fixture, project_fixture):
        input_data = [
            {
                'col1': 'a',
                'col2': 'b'
            },
            {
                'col1': 'c',
                'col2': 'd',
            }

        ]
        test_execution.settings = settings_manager.get_project_settings(testdir_fixture['path'],
                                                                        project_fixture['name'])
        test_execution.settings['test_data'] = 'csv'

        test_case.new_test_case(testdir_fixture['path'],
                                project_fixture['name'],
                                [],
                                'test_get_data')
        test_data.save_external_test_data_file(testdir_fixture['path'],
                                               project_fixture['name'],
                                               'test_get_data',
                                               input_data)
        returned_data = test_data.get_test_data(testdir_fixture['path'],
                                                project_fixture['name'],
                                                'test_get_data')
        assert returned_data == input_data


class Test_get_internal_test_data:

    def test_get_internal_test_data(self, testdir_fixture, project_fixture):
        test_name = 'test_get_internal_test_data'
        input_data = [
            {
                'col1': "'a'",
                'col2': "'b'"
            },
            {
                'col1': "'c'",
                'col2': "'d'",
            }

        ]
        test_case.new_test_case(testdir_fixture['path'],
                                project_fixture['name'],
                                [],
                                test_name)
        test_steps = {
            'setup': [],
            'test': [],
            'teardown': []
        }
        test_execution.settings = settings_manager.get_project_settings(testdir_fixture['path'],
                                                                        project_fixture['name'])
        test_execution.settings['test_data'] = 'infile'

        test_case.save_test_case(testdir_fixture['path'], project_fixture['name'],
                                 test_name, '', [], test_steps, input_data)
        
        internal_data = test_data.get_internal_test_data(testdir_fixture['path'],
                                                         project_fixture['name'],
                                                         test_name)
        assert internal_data == input_data
