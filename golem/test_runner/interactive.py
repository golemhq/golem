"""Golem interactive mode."""
from golem.core import utils, settings_manager, session
from golem import execution
from golem import actions
from golem.gui import gui_utils
from .execution_runner import define_browsers
from golem.test_runner import execution_logger


def interactive(settings, cli_browsers):
    """Starts the Golem interactive shell."""
    browsers = utils.choose_browser_by_precedence(
        cli_browsers=cli_browsers, suite_browsers=[],
        settings_default_browser=settings['default_browser'])
    execution.browser_name = browsers[0]
    remote_browsers = settings_manager.get_remote_browsers(session.settings)
    default_browsers = gui_utils.get_supported_browsers_suggestions()
    browser_defs = define_browsers(browsers, remote_browsers, default_browsers)
    execution.browser_definition = browser_defs[0]
    execution.settings = settings
    execution.settings['interactive'] = True
    execution.logger = execution_logger.get_logger(
        cli_log_level=execution.settings['cli_log_level'],
        log_all_events=execution.settings['log_all_events'])
    actions.interactive_mode()
