"""Golem interactive mode."""
from golem.core import utils, settings_manager, test_execution
from golem import execution
from golem import actions
from golem import browser
from golem.gui import gui_utils
from .start_execution import define_drivers
from golem.test_runner import execution_logger


def interactive(settings, cli_drivers):
    """Starts the Golem interactive shell."""
    drivers = utils.choose_driver_by_precedence(cli_drivers=cli_drivers,
                                                suite_drivers=[],
                                                settings_default_driver=settings['default_browser'])
    execution.browser_name = drivers[0]
    remote_browsers = settings_manager.get_remote_browsers(test_execution.settings)
    default_browsers = gui_utils.get_supported_browsers_suggestions()
    browser_defs = define_drivers(drivers, remote_browsers, default_browsers)
    execution.browser_definition = browser_defs[0]
    execution.settings = settings
    execution.settings['interactive'] = True
    execution.logger = execution_logger.get_logger(console_log_level=execution.settings['console_log_level'],
                                                   log_all_events=execution.settings['log_all_events'])
    actions.debug()
