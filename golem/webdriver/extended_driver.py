from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (NoAlertPresentException,
                                        TimeoutException)

from golem.webdriver import common
from golem.webdriver.extended_webelement import ExtendedWebElement
from golem.webdriver import golem_expected_conditions as gec

from typing import List


class GolemExtendedDriver():

    def find(self, *args, **kwargs) -> ExtendedWebElement:
        if len(args) == 1:
            kwargs['element'] = args[0]
        return common._find(self, **kwargs)

    def find_all(self, *args, **kwargs) -> List[ExtendedWebElement]:
        if len(args) == 1:
            kwargs['element'] = args[0]
        return common._find_all(self, **kwargs)

    def navigate(self, url):
        self.get(url)

    # def drag_and_drop(self, element, target):
    #     actionChains = ActionChains(self)
    #     source_element = self.find(element)
    #     target_element = self.find(target)
    #     actionChains.drag_and_drop(source_element, target_element).perform()

    def alert_is_present(self):
        """an alert is present"""
        try:
            self.switch_to.alert
            return True
        except NoAlertPresentException:
            return False

    def wait_for_alert_present(self, timeout):
        """Wait for an alert to be present"""
        wait = WebDriverWait(self, timeout)
        message = 'Timeout waiting for alert to be present'
        wait.until(ec.alert_is_present(), message=message)

    def wait_for_element_present(self, element, timeout):
        """Wait for element present in the DOM"""
        self.find(element, timeout=timeout, wait_displayed=False)

    def wait_for_element_not_present(self, element, timeout):
        """Wait for element present in the DOM"""
        element = self.find(element, timeout=0)
        wait = WebDriverWait(self, timeout)
        message = ('Timeout waiting for element {} to not be present'
                   .format(element.name))
        wait.until(ec.staleness_of(element), message=message)

    def wait_for_element_enabled(self, element, timeout):
        """Wait for element to be enabled"""
        element = self.find(element, timeout=0)
        wait = WebDriverWait(self, timeout)
        message = 'Timeout waiting for element {} to be enabled'.format(element.name)
        wait.until(gec.element_to_be_enabled(element), message=message)
