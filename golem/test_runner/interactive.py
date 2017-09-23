import golem.core
from golem import actions


def interactive(settings, driver):
    golem.core.driver_name = driver
    golem.core.set_settings(settings)
    actions.debug()