from golem.core import utils, test_data, test_case

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
        test_case.new_test_case(testdir_fixture['path'],
                                project_fixture['name'],
                                [],
                                'test_get_data')
        test_data.save_test_data(testdir_fixture['path'],
                                 project_fixture['name'],
                                 'test_get_data',
                                 input_data)
        returned_data = test_data.get_test_data(testdir_fixture['path'],
                                                project_fixture['name'],
                                                'test_get_data')
        assert returned_data == input_data
