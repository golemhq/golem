from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select as SeleniumSelect

from golem.webdriver.common import _find, _find_all

from typing import List


def extend_webelement(web_element):
    """Extend the selenium WebElement using the
    ExtendedWebElement class
    """
    web_element.__class__ = ExtendedWebElement
    return web_element


class ExtendedWebElement(WebElement):

    def find(self, *args, **kwargs) -> 'ExtendedWebElement':
        if len(args) == 1:
            kwargs['element'] = args[0]
        return _find(self, **kwargs)

    def find_all(self, *args, **kwargs) -> List['ExtendedWebElement']:
        if len(args) == 1:
            kwargs['element'] = args[0]
        return _find_all(self, **kwargs)

    def double_click(self):
        """Double click the element"""
        action_chains = ActionChains(self.parent)
        action_chains.double_click(self).perform()

    def focus(self):
        """Give focus to element"""
        self.parent.execute_script('arguments[0].focus();', self)

    def has_focus(self):
        """Focus element"""
        script = 'return arguments[0] == document.activeElement'
        return self.parent.execute_script(script, self)

    def javascript_click(self):
        """Click element using Javascript"""
        self.parent.execute_script('arguments[0].click();', self)

    def mouse_over(self):
        """Mouse over element"""
        action_chains = ActionChains(self.parent)
        action_chains.move_to_element(self).perform()

    def press_key(self, key):
        """Press a key on element

        Examples:
          element.press_key('ENTER')
          element.press_key('TAB')
          element.press_key('LEFT')
        """
        if hasattr(Keys, key):
            key_attr = getattr(Keys, key)
            self.send_keys(key_attr)
        else:
            defined_keys = [name for name in dir(Keys) if
                            not name.startswith('_')]
            error_msg = ('Key {} is invalid\n'
                         'valid options are:\n'
                         '{}'.format(key, ','.join(defined_keys)))
            raise ValueError(error_msg)

    @property
    def select(self):
        """Return a Select object"""
        return Select(self)

    @property
    def value(self):
        """The value attribute of element"""
        return self.get_attribute('value')

    def has_attribute(self, attribute):
        """Element has attribute"""
        return self.get_attribute(attribute) is not None


class Select(SeleniumSelect):

    pass