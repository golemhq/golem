"""This module contains the methods for running a suite of tests and
a single test case.
The multiprocess_executor method runs all the test cases provided in
parallel using multiprocessing.
The test_runner method is in charge of executing a single test case.
"""

import os
import sys
import time
import traceback
from multiprocessing import Pool
from multiprocessing.pool import ApplyResult

import golem.core
from golem.core import (utils,
                        test_execution,
                        logger,
                        selenium_utils,
                        report,
                        actions)

def test_runner(workspace, project, test_case_name, test_data, suite_name,
                suite_data, suite_timestamp, settings):
    ''' runs a single test case by name'''
    result = {
        'result': 'pass',
        'error': None,
        'description': None,
        'steps': None,
        'test_elapsed_time': None,
        'test_timestamp': None}

    import execution_logger
    instance = None
    test_timestamp = utils.get_timestamp()
    test_start_time = time.time()

    golem.core.set_settings(settings)

    # create a directory to store report.json and screenshots
    report_directory = report.create_report_directory(workspace,
                                                      project,
                                                      test_case_name,
                                                      suite_name,
                                                      suite_timestamp)
    try:
        test_class = utils.get_test_case_class(
                        project,
                        test_case_name)
        instance = test_class()

        if hasattr(instance, 'setup'):
            instance.setup()
        else:
            raise Exception

        if hasattr(instance, 'test'):
            instance.test(test_data)
        else:
            raise Exception

    except:
        result['result'] = 'fail'
        result['error'] = traceback.format_exc()
        if settings['screenshot_on_error']:
            actions.capture('error')
        print dir(traceback)
        print traceback.print_exc()

    try:
        if hasattr(instance, 'teardown'):
            instance.teardown()
        else:
            raise Exception
    except:
        result['result'] = 'fail'
        result['error'] = 'teardown failed'

    test_end_time = time.time()
    test_elapsed_time = round(test_end_time - test_start_time, 2)

    result['description'] = execution_logger.description
    result['steps'] = execution_logger.steps
    result['test_elapsed_time'] = test_elapsed_time
    result['test_timestamp'] = test_timestamp
    result['screenshots'] = execution_logger.screenshots

    report.generate_report(report_directory,
                           test_case_name,
                           test_data,
                           result)
    return result


def multiprocess_executor(execution_list, processes=1,
                          suite_name=None, suite_data=None):
    print 'execution list', execution_list
    timestamp = utils.get_timestamp()

    if not suite_name:
        suite_name = '__single__'

    pool = Pool(processes=processes)

    results = []
    for test in execution_list:
        apply_async = pool.apply_async(test_runner,
                                       args=(test_execution.root_path,
                                             test_execution.project,
                                             test[0],
                                             test[1],
                                             suite_name,
                                             suite_data,
                                             timestamp,
                                             test_execution.settings),
                                       callback=logger.log_result)
        results.append(apply_async)

    map(ApplyResult.wait, results)

    lst_results = [r.get() for r in results]

    #for res in lst_results:
    #    print '\none result\n',res

    pool.close()
    pool.join()


def run_single_test_case(workspace, project, full_test_case_name):

    # check if test case exists
    if not utils.test_case_exists(workspace, project, full_test_case_name):
        sys.exit(
            "ERROR: no test case named {} exists".format(full_test_case_name))
    else:
        # get test data
        data_sets = utils.get_test_data(workspace,
                                        project,
                                        full_test_case_name)
        execution_list = []
        if data_sets:
            for data_set in data_sets:
                execution_list.append((full_test_case_name, data_set))
        else:
            execution_list.append((full_test_case_name, {}))
        # run the single test, once for each data set
        multiprocess_executor(execution_list, 2)


def run_suite(workspace, project, full_suite_name):
    ''' a suite '''

    # TO DO implement directory suites

    if not utils.test_suite_exists(workspace, project, full_suite_name):
        sys.exit(
            "ERROR: no test suite named {} exists".format(full_suite_name))
    else:
        # get test case list
        test_case_list = utils.get_suite_test_cases(project,
                                                    full_suite_name)

        # get test data for each test case present in the suite 
        # and append tc/data pairs for each test case and for each data
        # set to execution list.
        # if there is no data for a test case, it is appended with an
        # empty dict
        execution_list = []
        for test_case in test_case_list:
            data_sets = utils.get_test_data(workspace,
                                            project,
                                            test_case)
            if data_sets:
                for data_set in data_sets:
                    execution_list.append((test_case, data_set))
            else:
                execution_list.append((test_case, {}))

    multiprocess_executor(execution_list, 1, suite_name=full_suite_name)
