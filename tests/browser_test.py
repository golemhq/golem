import pytest

from golem.gui import gui_utils
from golem import browser, execution
from golem.core import settings_manager
from golem.execution_runner import execution_runner
from golem.test_runner import test_logger


class TestGetBrowser:

    def test_driver_path_is_not_defined(self):
        execution.settings = settings_manager.assign_settings_default_values({})
        execution.logger = test_logger.get_logger()
        default_browsers = gui_utils.get_supported_browsers_suggestions()
        drivers = [
            ('chromedriver_path', 'chrome'),
            ('chromedriver_path', 'chrome-headless'),
            ('edgedriver_path', 'edge'),
            ('geckodriver_path', 'firefox'),
            ('iedriver_path', 'ie'),
            ('operadriver_path', 'opera'),
        ]
        for setting_path, browser_name in drivers:
            execution.browser_definition = execution_runner.define_browsers(
                [browser_name], [], default_browsers)[0]
            with pytest.raises(Exception) as excinfo:
                browser.open_browser()
                expected = 'Exception: {} setting is not defined'.format(setting_path)
                assert expected in str(excinfo.value)

    def test_executable_not_present(self):
        execution.settings = settings_manager.assign_settings_default_values({})
        execution.logger = test_logger.get_logger()
        default_browsers = gui_utils.get_supported_browsers_suggestions()
        drivers = [
            ('chromedriver_path', './drivers/chromedriver*', 'chrome'),
            ('chromedriver_path', './drivers/chromedriver*', 'chrome-headless'),
            ('edgedriver_path', './drivers/edgedriver*', 'edge'),
            ('geckodriver_path', './drivers/geckodriver*', 'firefox'),
            ('iedriver_path', './drivers/iedriver*', 'ie'),
            ('operadriver_path', './drivers/operadriver*', 'opera'),
        ]
        for setting_key, setting_path, browser_name in drivers:
            execution.browser_definition = execution_runner.define_browsers(
                [browser_name], [], default_browsers)[0]
            execution.settings[setting_key] = setting_path
            with pytest.raises(Exception) as excinfo:
                browser.open_browser()
                expected = 'No executable file found using path {}'.format(setting_path)
                assert expected in str(excinfo.value)
