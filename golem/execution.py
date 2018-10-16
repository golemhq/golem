"""The Execution module contains data specific to a
single test execution
"""

browser = None
browser_definition = None
browsers = {}
steps = []
data = None
description = None
errors = []
settings = None
project = None
workspace = None
report_directory = None
logger = None


def _reset():
    global browser
    global browser_definition
    global browsers
    global steps
    global data
    global description
    global errors
    global settings
    global project
    global workspace
    global report_directory
    global logger
    browser = None
    browser_definition = None
    browsers = {}
    steps = []
    description = None
    errors = []
    settings = None
    project = None
    workspace = None
    report_directory = None
    logger = None
