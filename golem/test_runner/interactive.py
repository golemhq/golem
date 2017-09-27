import golem.core
from golem.core import utils
from golem import actions
from golem.actions import *
from golem.selenium import *


def interactive(settings, cli_drivers):

    drivers = utils.choose_driver_by_precedence(cli_drivers=cli_drivers,
                                                suite_drivers=[],
                                                settings_default_driver=settings['default_driver'])
    golem.core.driver_name = drivers[0]
    golem.core.set_settings(settings)
    from golem.core import execution_logger
    execution_logger.get_logger()
    actions.debug()