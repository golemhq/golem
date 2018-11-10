import os

from golem.core import environment_manager


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


class TestGetEnvs:

    def test_get_envs(self, project_session):
        testdir = project_session.testdir
        project = project_session.name
        env_json_path = os.path.join(testdir, 'projects',
                                     project, 'environments.json')
        with open(env_json_path, 'w') as env_json_file:
            env_json_file.write(ENV_DATA)
        envs = environment_manager.get_envs(testdir, project)
        assert len(envs) == 2
        assert 'test' in envs
        assert 'development' in envs

    def test_get_envs_empty_file(self, project_session):
        testdir = project_session.testdir
        project = project_session.name
        env_json_path = os.path.join(testdir, 'projects',
                                     project, 'environments.json')
        with open(env_json_path, 'w') as env_json_file:
            env_json_file.write('')
        envs = environment_manager.get_envs(testdir, project)
        assert envs == []

    def test_get_envs_invalid_json(self, project_session):
        testdir = project_session.testdir
        project = project_session.name
        env_json_path = os.path.join(testdir, 'projects',
                                     project, 'environments.json')
        with open(env_json_path, 'w') as env_json_file:
            env_json_file.write(ENV_DATA_INVALID_JSON)
        envs = environment_manager.get_envs(testdir, project)
        expected_envs = []
        assert envs == expected_envs

    def test_get_envs_file_not_exist(self, project_session):
        testdir = project_session.testdir
        project = project_session.name
        env_json_path = os.path.join(testdir, 'projects',
                                     project, 'environments.json')
        if os.path.isfile(env_json_path):
            os.remove(env_json_path)
        envs = environment_manager.get_envs(testdir, project)
        expected_envs = []
        assert envs == expected_envs


class TestGetEnvironmentData:

    def test_get_environment_data(self, project_session):
        testdir = project_session.testdir
        project = project_session.name
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

    def test_get_environment_data_empty_file(self, project_session):
        testdir = project_session.testdir
        project = project_session.name
        env_json_path = os.path.join(testdir, 'projects',
                                     project, 'environments.json')
        with open(env_json_path, 'w') as env_json_file:
            env_json_file.write('')
        result = environment_manager.get_environment_data(testdir, project)
        assert result == {}

    def test_get_environment_data_invalid_json(self, project_session):
        testdir = project_session.testdir
        project = project_session.name
        env_json_path = os.path.join(testdir, 'projects',
                                     project, 'environments.json')
        with open(env_json_path, 'w') as env_json_file:
            env_json_file.write(ENV_DATA_INVALID_JSON)
        result = environment_manager.get_environment_data(testdir, project)
        assert result == {}

    def test_get_environment_data_file_not_exist(self, project_function):
        testdir = project_function.testdir
        project = project_function.name
        result = environment_manager.get_environment_data(testdir, project)
        assert result == {}


class TestGetEnvironmentsAsString:

    def test_get_environments_as_string(self, project_session):
        testdir = project_session.testdir
        project = project_session.name
        env_json_path = os.path.join(testdir, 'projects', project, 'environments.json')
        with open(env_json_path, 'w') as env_json_file:
            env_json_file.write(ENV_DATA)
        result = environment_manager.get_environments_as_string(testdir, project)
        assert result == ENV_DATA

    def test_get_environments_as_string_empty_file(self, project_session):
        project = project_session.name
        testdir = project_session.testdir
        env_json_path = os.path.join(testdir, 'projects', project, 'environments.json')
        with open(env_json_path, 'w') as env_json_file:
            env_json_file.write('')
        result = environment_manager.get_environments_as_string(testdir, project)
        assert result == ''

    def test_get_environments_as_string_file_not_exist(self, project_function):
        project = project_function.name
        testdir = project_function.testdir
        path = os.path.join(testdir, 'projects', project, 'environments.json')
        os.remove(path)
        result = environment_manager.get_environments_as_string(testdir, project)
        assert result == ''


class TestSaveEnvironments:

    def test_save_environments(self, project_session):
        project = project_session.name
        testdir = project_session.testdir
        error = environment_manager.save_environments(testdir, project, ENV_DATA)
        assert error == ''
        env_json_path = os.path.join(testdir, 'projects', project, 'environments.json')
        with open(env_json_path) as json_file:
            file_content = json_file.read()
            assert file_content == ENV_DATA

    def test_save_environments_empty_env_data(self, project_session):
        project = project_session.name
        testdir = project_session.testdir
        error = environment_manager.save_environments(testdir, project, '')
        assert error == ''
        env_json_path = os.path.join(testdir, 'projects', project, 'environments.json')
        with open(env_json_path) as json_file:
            file_content = json_file.read()
            assert file_content == ''

    def test_save_environments_invalid_json(self, project_function):
        project = project_function.name
        testdir = project_function.testdir
        env_json_path = os.path.join(testdir, 'projects', project, 'environments.json')
        original_json = '{"test": "value"}'
        with open(env_json_path, 'w') as json_file:
            json_file.write(original_json)
        error = environment_manager.save_environments(testdir, project,
                                                      ENV_DATA_INVALID_JSON)
        assert error == 'must be valid JSON'
        # assert the original environments.json file was not modified
        with open(env_json_path) as json_file:
            file_content = json_file.read()
            assert file_content == original_json
