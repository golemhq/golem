""" The Execution class contains data specific of a single execution
that must be shared among other modules such as the test data, the webdriver
object, etc.
The instance of Execution is added to sys.modules to simplify the public API.
"""
import sys


class Execution:

    def __init__(self):
        self.driver = None
        self.steps = []
        self.driver_name = None
        self.settings = None
        self.project = None
        self.workspace = None
        self.data = None
        self.report_directory = None
        self.description = None
        self.steps = []
        self.logger = None


sys.modules['golem.execution'] = Execution()
