""" Stored values specific to a single test execution. """

test_file = None
browser = None
browser_definition = None
browsers = {}
data = None
secrets = None
description = None
settings = None
test_dirname = None
test_path = None
project_name = None
project_path = None
testdir = None
execution_reportdir = None
testfile_reportdir = None
logger = None
tags = []
environment = None

# values below correspond to the current running test function
test_name = None
steps = []
errors = []
test_reportdir = None
timers = {}
