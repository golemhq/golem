"""
"""
import sys

from golem.core import test_execution, utils, report
from golem.test_runner.multiprocess_executor import multiprocess_executor, run_test


# def run_single_test_case(workspace, project, full_test_name):

#     # check if test case exists
#     if not utils.test_case_exists(workspace, project, full_test_name):
#         sys.exit(
#             "ERROR: no test case named {} exists".format(full_test_name))
#     else:
#         threads = 1
#         if test_execution.thread_amount:
#             threads = test_execution.thread_amount
        
#         execution_list = []

#         drivers = []

#         if test_execution.drivers:
#             drivers = test_execution.drivers

#         if not drivers and 'default_driver' in test_execution.settings:
#             drivers = [test_execution.settings['default_driver']]

#         if not drivers:
#             drivers = ['firefox']

#         # get test data
#         data_sets = utils.get_test_data(workspace,
#                                         project,
#                                         full_test_name)
#         if not data_sets:
#             data_sets = [{}]
        
#         for data_set in data_sets:
#             for driver in drivers:
#                 execution_list.append({
#                     'test_name': full_test_name,
#                     'data_set': data_set,
#                     'driver': driver,
#                     })

#         # run the single test, once for each data set
#         multiprocess_executor(execution_list, threads)


def run_test_or_suite(workspace, project, test=None, suite=None, directory_suite=None):
    '''run a test, a suite or a "directory suite"'''

    test_list = []
    threads = 1
    suite_amount_workers = None
    suite_drivers = None
    drivers = []

    # get test list
    if test:
        test_list = [test]
    elif suite:
        test_list = utils.get_suite_test_cases(workspace, project, suite)      
        suite_amount_workers = utils.get_suite_amount_of_workers(workspace, project, suite)
        suite_drivers = utils.get_suite_browsers(workspace, project, suite)
    elif directory_suite:
        test_list = utils.get_directory_suite_test_cases(workspace, project, directory_suite)
        suite = directory_suite
    else:
        sys.exit("ERROR: invalid arguments for run_test_or_suite()")

    # get threads
    if test_execution.thread_amount:
        # the thread count passed through cli has higher priority
        threads = test_execution.thread_amount
    elif suite_amount_workers:
        threads = suite_amount_workers
    
    # get drivers
    if test_execution.drivers:
        drivers = test_execution.drivers
    elif suite_drivers:
        drivers = suite_drivers
    elif not drivers and 'default_driver' in test_execution.settings:
        drivers = [test_execution.settings['default_driver']]
    else:
        drivers = ['chrome']

    # timestamp is passed when the test is executed from the GUI,
    # otherwise, a timestamp should be generated at this point
    # the timestamp is used to identify this unique execution of the test or suite
    if not test_execution.timestamp:
        test_execution.timestamp = utils.get_timestamp()

    # get test data for each test present in the list of tests
    # for each test in the list, for each data set and driver combination
    # append an entry to the execution_list dictionary
    execution_list = []
    for test_case in test_list:
        data_sets = utils.get_test_data(workspace, project, test_case)
        for data_set in data_sets:
            for driver in drivers:
                execution_list.append(
                    {
                        'test_name': test_case,
                        'data_set': vars(data_set),
                        'driver': driver,
                        'report_directory': None
                    }
                )

    # 
    for test in execution_list:
        # generate a report directory for this test
        report_directory = report.create_report_directory(test_execution.root_path,
                                                          test_execution.project,
                                                          test['test_name'],
                                                          suite, 
                                                          test_execution.timestamp)
        test['report_directory'] = report_directory

    debug = test_execution.debug

    if debug:
        if threads == 1 and len(execution_list) == 1:
            # run single test without threading
            test = execution_list[0]
            run_test(test_execution.root_path, test_execution.project,
                     test['test_name'], test['data_set'],
                     test['driver'], test_execution.settings,
                     test['report_directory'])
        else:
            print('Error: to run in debug mode, only one test in a single thread is required')
    else:
        # run list of tests using threading
        multiprocess_executor(execution_list, threads, suite_name=suite)
