"""This module defines the exceptions used by the test cases"""


class IncorrectSelectorType(Exception):
    pass


class ElementNotFound(Exception):
    pass


class TestError(Exception):
    pass


class TestFailure(Exception):
    pass


class TextNotPresent(Exception):
    pass


class ElementNotDisplayed(Exception):
    pass