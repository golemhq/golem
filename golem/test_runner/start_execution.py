"""
"""
import sys

from golem.core import test_execution, utils, report
from golem.test_runner.multiprocess_executor import multiprocess_executor, run_test


def run_test_or_suite(workspace, project, test=None, suite=None, directory_suite=None):
    '''run a test, a suite or a "directory suite"'''

    tests = []
    threads = 1
    suite_amount_workers = None
    suite_drivers = None
    drivers = []
    suite_module = None
    report_suite_name = None
    is_suite = False

    # get test list
    if test:
        tests = [test]
        report_suite_name = 'single_tests'
    elif suite:
        tests = utils.get_suite_test_cases(workspace, project, suite)
        suite_amount_workers = utils.get_suite_amount_of_workers(workspace, project, suite)
        suite_drivers = utils.get_suite_browsers(workspace, project, suite)
        suite_module = utils.get_suite_module(test_execution.root_path,
                                              test_execution.project,
                                              suite)
        report_suite_name = suite
        is_suite = True
    elif directory_suite:
        tests = utils.get_directory_suite_test_cases(workspace, project, directory_suite)
        report_suite_name = directory_suite
        is_suite = True
    else:
        sys.exit("ERROR: invalid arguments for run_test_or_suite()")

    # get threads
    if test_execution.thread_amount:
        # the thread count passed through cli has higher priority
        threads = test_execution.thread_amount
    elif suite_amount_workers:
        threads = suite_amount_workers

    settings_default_driver = test_execution.settings['default_browser']
    drivers = utils.choose_driver_by_precedence(cli_drivers=test_execution.cli_drivers,
                                                suite_drivers=suite_drivers,
                                                settings_default_driver=settings_default_driver)

    # timestamp is passed when the test is executed from the GUI,
    # otherwise, a timestamp should be generated at this point
    # the timestamp is used to identify this unique execution of the test or suite
    if not test_execution.timestamp:
        test_execution.timestamp = utils.get_timestamp()

    # get test data for each test present in the list of tests
    # for each test in the list, for each data set and driver combination
    # append an entry to the execution_list
    execution_list = []
    for test_case in tests:
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
    if is_suite:
        execution_directory = report.create_suite_execution_directory(test_execution.root_path,
                                                                      test_execution.project,
                                                                      report_suite_name,
                                                                      test_execution.timestamp)
    else:
        execution_directory = report.create_test_execution_directory(test_execution.root_path,
                                                                     test_execution.project,
                                                                     test,
                                                                     test_execution.timestamp)
    #
    for test in execution_list:
        # generate a report directory for this test
        report_directory = report.create_report_directory(execution_directory,
                                                          test['test_name'],
                                                          is_suite)
        test['report_directory'] = report_directory


    if suite:
        if hasattr(suite_module, 'before'):
            suite_module.before()

    if test_execution.interactive and threads == 1:
        if threads == 1:
            # run tests serially
            for test in execution_list:
                run_test(test_execution.root_path, test_execution.project,
                         test['test_name'], test['data_set'],
                         test['driver'], test_execution.settings,
                         test['report_directory'])
        else:
            print('Error: to run in debug mode, threads must equal one')
    else:
        # run list of tests using threading
        multiprocess_executor(execution_list, is_suite, execution_directory, threads)

    if suite:
        if hasattr(suite_module, 'after'):
            suite_module.after()
