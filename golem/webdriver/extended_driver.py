from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from golem.webdriver import common
from golem.webdriver.extended_webelement import ExtendedWebElement

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
        wait.until(ec.alert_is_present())


