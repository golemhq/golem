import os

from tests import helper_functions
from golem.core import environment_manager

from tests.fixtures import testdir_fixture, permanent_project_fixture


ENV_DATA = ('{\n'
            '    "test": {\n'
            '        "url": "http://localhost:8000"\n'
            '    },\n'
            '    "development": {\n'
            '        "url": "http://localhost:8001"\n'
            '    }\n'
            '}')

ENV_DATA_INVALID_JSON = ('{\n'
    '    \'test\': {\n'
    '        "url": "http://localhost:8000"\n'
    '    }\n'
    '}')


class Test_get_envs:

    def test_get_envs(self, permanent_project_fixture):
        project = permanent_project_fixture['name']
        testdir = permanent_project_fixture['testdir']
        env_json_path = os.path.join(testdir, 'projects',
                                     project, 'environments.json')

        with open(env_json_path, 'w') as env_json_file:
            env_json_file.write(ENV_DATA)
        envs = environment_manager.get_envs(testdir, project)
        expected_envs = ['test', 'development']
        assert envs == expected_envs


    def test_get_envs_empty_file(self, permanent_project_fixture):
        project = permanent_project_fixture['name']
        testdir = permanent_project_fixture['testdir']
        env_json_path = os.path.join(testdir, 'projects',
                                     project, 'environments.json')
        with open(env_json_path, 'w') as env_json_file:
            env_json_file.write('')
        envs = environment_manager.get_envs(testdir, project)
        expected_envs = []
        assert envs == expected_envs


    def test_get_envs_invalid_json(self, permanent_project_fixture):
        project = permanent_project_fixture['name']
        testdir = permanent_project_fixture['testdir']
        env_json_path = os.path.join(testdir, 'projects',
                                     project, 'environments.json')
        with open(env_json_path, 'w') as env_json_file:
            env_json_file.write(ENV_DATA_INVALID_JSON)
        envs = environment_manager.get_envs(testdir, project)
        expected_envs = []
        assert envs == expected_envs


    def test_get_envs_file_not_exist(self, permanent_project_fixture):
        project = permanent_project_fixture['name']
        testdir = permanent_project_fixture['testdir']
        env_json_path = os.path.join(testdir, 'projects',
                                     project, 'environments.json')
        if os.path.isfile(env_json_path):
            os.remove(env_json_path)
        envs = environment_manager.get_envs(testdir, project)
        expected_envs = []
        assert envs == expected_envs


class Test_get_environment_data:

    def test_get_environment_data(self, permanent_project_fixture):
        project = permanent_project_fixture['name']
        testdir = permanent_project_fixture['testdir']
        env_json_path = os.path.join(testdir, 'projects',
                                     project, 'environments.json')
        with open(env_json_path, 'w') as env_json_file:
            env_json_file.write(ENV_DATA)
        result = environment_manager.get_environment_data(testdir, project)
        expected = {
                    "test": {
                        "url": "http://localhost:8000"
                        },
                    "development": {
                        "url": "http://localhost:8001"
                        }
                    }
        assert result == expected


    def test_get_environment_data_empty_file(self, permanent_project_fixture):
        project = permanent_project_fixture['name']
        testdir = permanent_project_fixture['testdir']
        env_json_path = os.path.join(testdir, 'projects',
                                     project, 'environments.json')
        with open(env_json_path, 'w') as env_json_file:
            env_json_file.write('')
        result = environment_manager.get_environment_data(testdir, project)
        expected = {}
        assert result == expected


    def test_get_environment_data_invalid_json(self, permanent_project_fixture):
        project = permanent_project_fixture['name']
        testdir = permanent_project_fixture['testdir']
        env_json_path = os.path.join(testdir, 'projects',
                                     project, 'environments.json')
        with open(env_json_path, 'w') as env_json_file:
            env_json_file.write(ENV_DATA_INVALID_JSON)
        result = environment_manager.get_environment_data(testdir, project)
        expected = {}
        assert result == expected


    def test_get_environment_data_file_not_exist(self, permanent_project_fixture):
        project = permanent_project_fixture['name']
        testdir = permanent_project_fixture['testdir']
        env_json_path = os.path.join(testdir, 'projects',
                                     project, 'environments.json')
        if os.path.isfile(env_json_path):
            os.remove(env_json_path)
        result = environment_manager.get_environment_data(testdir, project)
        expected = {}
        assert result == expected


class Test_get_environments_as_string:

    def test_get_environments_as_string(self, permanent_project_fixture):
        project = permanent_project_fixture['name']
        testdir = permanent_project_fixture['testdir']
        env_json_path = os.path.join(testdir, 'projects',
                                     project, 'environments.json')
        with open(env_json_path, 'w') as env_json_file:
            env_json_file.write(ENV_DATA)
        result = environment_manager.get_environments_as_string(testdir, project)
        assert result == ENV_DATA


    def test_get_environments_as_string_empty_file(self, permanent_project_fixture):
        project = permanent_project_fixture['name']
        testdir = permanent_project_fixture['testdir']
        env_json_path = os.path.join(testdir, 'projects',
                                     project, 'environments.json')
        with open(env_json_path, 'w') as env_json_file:
            env_json_file.write('')
        result = environment_manager.get_environments_as_string(testdir, project)
        assert result == ''


    def test_get_environments_as_string_file_not_exist(self, permanent_project_fixture):
        project = permanent_project_fixture['name']
        testdir = permanent_project_fixture['testdir']
        env_json_path = os.path.join(testdir, 'projects',
                                     project, 'environments.json')
        if os.path.isfile(env_json_path):
            os.remove(env_json_path)
        result = environment_manager.get_environments_as_string(testdir, project)
        assert result == ''


class Test_save_environments:

    def test_save_environments(self, permanent_project_fixture):
        project = permanent_project_fixture['name']
        testdir = permanent_project_fixture['testdir']
        env_json_path = os.path.join(testdir, 'projects',
                                     project, 'environments.json')
        error = environment_manager.save_environments(testdir, project, ENV_DATA)
        assert error == ''
        with open(env_json_path) as json_file:
            file_content = json_file.read()
            assert file_content == ENV_DATA


    def test_save_environments_empty_env_data(self, permanent_project_fixture):
        project = permanent_project_fixture['name']
        testdir = permanent_project_fixture['testdir']
        env_json_path = os.path.join(testdir, 'projects',
                                     project, 'environments.json')
        empty_env_data = ''
        error = environment_manager.save_environments(testdir, project,
                                                      empty_env_data)
        assert error == ''
        with open(env_json_path) as json_file:
            file_content = json_file.read()
            assert file_content == empty_env_data


    def test_save_environments_invalid_json(self, permanent_project_fixture):
        project = permanent_project_fixture['name']
        testdir = permanent_project_fixture['testdir']
        env_json_path = os.path.join(testdir, 'projects',
                                     project, 'environments.json')
        original_json = '{"test": ""}'
        with open(env_json_path, 'w') as json_file:
            file_content = json_file.write(original_json)
        error = environment_manager.save_environments(testdir, project,
                                                      ENV_DATA_INVALID_JSON)
        assert error == 'must be valid JSON'
        # assert the original environments.json file was not modified
        with open(env_json_path) as json_file:
            file_content = json_file.read()
            assert file_content == original_json