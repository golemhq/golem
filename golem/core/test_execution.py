from multiprocessing import Manager

"""A list of variables used for the current execution"""
root_path = None

project = None

settings = {}

# Multiprocess safe indicator if any test has failed during execution
has_failed_tests = Manager().Value('error', False)
