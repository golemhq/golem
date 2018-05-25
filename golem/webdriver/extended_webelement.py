from selenium.webdriver.remote.webelement import WebElement

from golem.webdriver import common


def extend_webelement(web_element):
    """Extend the selenium WebElement using the
    ExtendedWebElement class
    """
    web_element.__class__ = ExtendedWebElement
    return web_element


class ExtendedWebElement(WebElement):

    def find(self, *args, **kwargs):
        if len(args) == 1:
            kwargs['element'] = args[0]
        return common._find(self, **kwargs)

    def find_all(self, *args, **kwargs):
        if len(args) == 1:
            kwargs['element'] = args[0]
        return common._find_all(self, **kwargs)
