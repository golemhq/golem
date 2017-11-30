""" The Execution class contains data specific of a single test execution
that is shared among other modules.

"""
import sys


class Execution:

    def __init__(self):
        self.browser = None
        # self.browser_name = None
        self.browser_definition = None
        self.browsers = {}
        self.steps = []
        self.data = None
        self.description = None
        self.settings = None
        self.project = None
        self.workspace = None
        self.report_directory = None
        self.logger = None

# The instance of Execution is added to sys.modules to simplify the public API.
sys.modules['golem.execution'] = Execution()
