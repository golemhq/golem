import sys


# driver = None

# driver_name = None
# settings = None
# project = None
# workspace = None

# # data object used in the execution
# data = None

# report_directory = None
# description = None

# # list of steps gathered throughout the execution
# steps = []



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
