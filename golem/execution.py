"""The Execution module contains data specific to a
single test execution
"""

browser = None
browser_definition = None
browsers = {}
steps = []
data = None
secrets = None
description = None
errors = []
settings = None
project = None
testdir = None
report_directory = None
logger = None
timers = {}
tags = []


def _reset():
    global browser
    global browser_definition
    global browsers
    global steps
    global data
    global secrets
    global description
    global errors
    global settings
    global project
    global testdir
    global report_directory
    global logger
    global timers
    global tags
    browser = None
    browser_definition = None
    browsers = {}
    steps = []
    description = None
    errors = []
    settings = None
    project = None
    testdir = None
    report_directory = None
    logger = None
    timers = {}
    tags = []
