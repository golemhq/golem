"""This module defines the exceptions used by the test cases"""

class CommandException(Exception):
    pass


class IncorrectSelectorType(Exception):
    pass


class ElementNotFound(Exception):
    pass


class TextNotPresent(Exception):
    pass
