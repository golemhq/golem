import os

from golem.core import settings_manager


class TestCreateGlobalSettingsFile:

    def test_create_global_settings_file(self, testdir_class):
        settings_path = os.path.join(testdir_class.path, 'settings.json')
        os.remove(settings_path)
        settings_manager.create_global_settings_file(testdir_class.path)
        with open(settings_path) as settings_file:
            actual = settings_file.read()
            assert actual == settings_manager.SETTINGS_FILE_CONTENT
    

class TestCreateProjectSettingsFile:

    def test_create_project_settings_file(self, project_class):
        testdir = project_class.testdir
        project = project_class.name
        settings_path = os.path.join(testdir, 'projects', project, 'settings.json')
        os.remove(settings_path)
        settings_manager.create_project_settings_file(testdir, project)
        with open(settings_path) as settings_file:
            actual = settings_file.read()
            assert actual == settings_manager.REDUCED_SETTINGS_FILE_CONTENT


class TestReadJsonWithComments:

    def test__read_json_with_comments(self, testdir_class):
        file_content = ('{\n'
                        '// a commented line\n'
                        '"search_timeout": 10,\n'
                        '\n'
                        '// another commented line\n'
                        '"screenshot_on_error": true\n'
                        '}')
        path = os.path.join(testdir_class.path, 'temp_settings01.json')
        with open(path, 'w') as json_file:
            json_file.write(file_content)
        result = settings_manager._read_json_with_comments(path)
        expected = {
            'search_timeout': 10,
            'screenshot_on_error': True
        }
        assert result == expected


class TestAssignSettingsDefaultValues:

    def test_assign_settings_default_values_all_missing(self):
        normalized = settings_manager.assign_settings_default_values({})
        expected = {
            'search_timeout': 0,
            'wait_displayed': False,
            'screenshot_on_error': True,
            'screenshot_on_step': False,
            'screenshot_on_end': False,
            'test_data': 'csv',
            'wait_hook': None,
            'default_browser': 'chrome',
            'chromedriver_path': None,
            'edgedriver_path': None,
            'geckodriver_path': None,
            'iedriver_path': None,
            'operadriver_path': None,
            'remote_url': None,
            'remote_browsers': {},
            'console_log_level': 'INFO',
            'log_all_events': True,
            'start_maximized': True
        }
        assert normalized == expected

    def test_assign_settings_default_values_all_none(self):
        input_settings = {
            'search_timeout': None,
            'wait_displayed': None,
            'screenshot_on_error': None,
            'screenshot_on_step': None,
            'screenshot_on_end': None,
            'test_data': None,
            'wait_hook': None,
            'default_browser': None,
            'chromedriver_path': None,
            'edgedriver_path': None,
            'geckodriver_path': None,
            'iedriver_path': None,
            'operadriver_path': None,
            'remote_url': None,
            'remote_browsers': None,
            'console_log_level': None,
            'log_all_events': None,
            'start_maximized': None
        }
        normalized = settings_manager.assign_settings_default_values(input_settings)
        expected = {
            'search_timeout': 0,
            'wait_displayed': False,
            'screenshot_on_error': True,
            'screenshot_on_step': False,
            'screenshot_on_end': False,
            'test_data': 'csv',
            'wait_hook': None,
            'default_browser': 'chrome',
            'chromedriver_path': None,
            'edgedriver_path': None,
            'geckodriver_path': None,
            'iedriver_path': None,
            'operadriver_path': None,
            'remote_url': None,
            'remote_browsers': {},
            'console_log_level': 'INFO',
            'log_all_events': True,
            'start_maximized': True
        }
        assert normalized == expected

    def test_assign_settings_default_values_all_empty_str(self):
        input_settings = {
            'search_timeout': '',
            'wait_displayed': '',
            'screenshot_on_error': '',
            'screenshot_on_step': '',
            'screenshot_on_end': '',
            'test_data': '',
            'wait_hook': '',
            'default_browser': '',
            'chromedriver_path': '',
            'edgedriver_path': '',
            'geckodriver_path': '',
            'iedriver_path': '',
            'operadriver_path': '',
            'remote_url': '',
            'remote_browsers': '',
            'console_log_level': '',
            'log_all_events': '',
            'start_maximized': ''
        }
        normalized = settings_manager.assign_settings_default_values(input_settings)
        expected = {
            'search_timeout': 0,
            'wait_displayed': False,
            'console_log_level': 'INFO',
            'default_browser': 'chrome',
            'chromedriver_path': None,
            'edgedriver_path': None,
            'geckodriver_path': None,
            'iedriver_path': None,
            'operadriver_path': None,
            'log_all_events': True,
            'remote_browsers': {},
            'remote_url': None,
            'screenshot_on_end': False,
            'screenshot_on_error': True,
            'screenshot_on_step': False,
            'test_data': 'csv',
            'wait_hook': None,
            'start_maximized': True
        }
        assert normalized == expected


class TestGetGlobalSettings:

    def test_get_global_settings_default(self, testdir_function):
        global_settings = settings_manager.get_global_settings(testdir_function.path)
        expected = {
            'console_log_level': 'INFO',
            'default_browser': 'chrome',
            'chromedriver_path': './drivers/chromedriver*',
            'edgedriver_path': './drivers/edgedriver*',
            'geckodriver_path': './drivers/geckodriver*',
            'iedriver_path': './drivers/iedriver*',
            'operadriver_path': './drivers/operadriver*',
            'search_timeout': 20,
            'wait_displayed': False,
            'log_all_events': True,
            'remote_browsers': {},
            'remote_url': 'http://localhost:4444/wd/hub',
            'screenshot_on_end': False,
            'screenshot_on_error': True,
            'screenshot_on_step': False,
            'test_data': 'csv',
            'wait_hook': None,
            'start_maximized': True
        }
        assert global_settings == expected


class TestGetGlobalSettingsAsString:

    def test_get_global_settings_as_string(self, testdir_session):
        global_settings = settings_manager.get_global_settings_as_string(testdir_session.path)
        expected = settings_manager.SETTINGS_FILE_CONTENT
        assert global_settings == expected


class TestGetProjectSettings:

    def test_get_project_settings_default(self, project_function_clean):
        testdir = project_function_clean.testdir
        project = project_function_clean.name
        project_settings = settings_manager.get_project_settings(testdir, project)
        expected = {            
            'console_log_level': 'INFO',
            'default_browser': 'chrome',
            'chromedriver_path': './drivers/chromedriver*',
            'edgedriver_path': './drivers/edgedriver*',
            'geckodriver_path': './drivers/geckodriver*',
            'iedriver_path': './drivers/iedriver*',
            'operadriver_path': './drivers/operadriver*',
            'search_timeout': 20,
            'wait_displayed': False,
            'log_all_events': True,
            'remote_browsers': {},
            'remote_url': 'http://localhost:4444/wd/hub',
            'screenshot_on_end': False,
            'screenshot_on_error': True,
            'screenshot_on_step': False,
            'test_data': 'csv',
            'wait_hook': None,
            'start_maximized': True
        }
        assert project_settings == expected

    # TODO: test project override global settings


class TestGetProjectSettingsAsString:

    def test_get_project_settings_as_string(self, project_session):
        project_settings = settings_manager.get_project_settings_as_string(
            project_session.testdir, project_session.name)
        expected = settings_manager.REDUCED_SETTINGS_FILE_CONTENT
        assert project_settings == expected


class TestSaveGlobalSettings:

    def test_save_global_settings(self, testdir_class):
        input_settings = ('// test\n'
                          '{\n'
                          '"test": "test"\n'
                          '}')
        settings_manager.save_global_settings(testdir_class.path, input_settings)
        actual = settings_manager.get_global_settings_as_string(testdir_class.path)
        assert actual == input_settings


class TestSaveProjectSettings:

    def test_save_project_settings(self, project_class):
        testdir = project_class.testdir
        project = project_class.name
        input_settings = ('// test\n'
                          '{\n'
                          '"test": "test"\n'
                          '}')
        settings_manager.save_project_settings(testdir, project, input_settings)
        actual = settings_manager.get_project_settings_as_string(testdir, project)
        assert actual == input_settings


class TestGetRemoteBrowsers:

    def test_get_remote_browsers(self):
        settings = {
            "remote_browsers": {
                "chrome_60_mac": {
                    "browserName": "chrome",
                    "version": "60.0",
                    "platform": "macOS 10.12"
                },
                "chrome_61_mac": {
                    "browserName": "chrome",
                    "version": "60.0",
                    "platform": "macOS 10.12"
                }
            }
        }
        expected = {
            "chrome_60_mac": {
                "browserName": "chrome",
                "version": "60.0",
                "platform": "macOS 10.12"
            },
            "chrome_61_mac": {
                "browserName": "chrome",
                "version": "60.0",
                "platform": "macOS 10.12"
            }
        }
        rb = settings_manager.get_remote_browsers(settings)
        assert rb == expected


class TestGetRemoteBrowserList:

    def test_get_remote_browser_list(self):
        input_settings = {
            'remote_browsers': {
                'browser01': {},
                'browser02': {}
            }
        }
        remote_browsers = settings_manager.get_remote_browser_list(input_settings)
        expected = ['browser01', 'browser02']
        assert sorted(remote_browsers) == sorted(expected)

    def test_get_remote_browser_list_empty(self):
        input_settings = {
            'another_setting': '',
            'remote_browsers': {}
        }
        remote_browsers = settings_manager.get_remote_browser_list(input_settings)
        expected = []
        assert remote_browsers == expected

    def test_get_remote_browser_list_not_present(self):
        input_settings = {
            'another_setting': ''
        }
        remote_browsers = settings_manager.get_remote_browser_list(input_settings)
        expected = []
        assert remote_browsers == expected
