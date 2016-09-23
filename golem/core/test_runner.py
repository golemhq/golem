"""This module contains the methods for running a suite of tests and
a single test case.
The multiprocess_executor method runs all the test cases provided in
parallel using multiprocessing.
The test_runner method is in charge of executing a single test case.
"""

import os
import sys
import traceback
from multiprocessing import Pool
from multiprocessing.pool import ApplyResult

from golem.core import utils, test_execution, logger, selenium_utils, report


def test_runner(project, test_case_name, test_data, suite_name, suite_data,
                timestamp):
    ''' runs a single test case by name'''

    result = {
        'result': 'pass',
        'error': None,
        'description': None,
        'steps': None,}

    import execution_logger
    instance = None

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

        if hasattr(instance, 'teardown'):
            instance.teardown()
        else:
            raise Exception
    except:
        result['result'] = 'fail'
        result['error'] = traceback.format_exc()
        print dir(traceback)
        print traceback.print_exc()

    result['description'] = execution_logger.description
    result['steps'] = execution_logger.steps

    report.generate_report(result,
                           test_execution.root_path,
                           project,
                           test_case_name,
                           test_data, suite_name,
                           timestamp)

    return result


def multiprocess_executor(execution_list, processes=1,
                          suite_name=None, suite_data=None):
    print execution_list
    timestamp = utils.get_timestamp()

    pool = Pool(processes=processes)

    results = []
    for test in execution_list:
        apply_async = pool.apply_async(test_runner,
                                       args=(test_execution.project,
                                             test[0],
                                             test[1],
                                             suite_name,
                                             suite_data,
                                             timestamp),
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
        for data_set in data_sets:
            execution_list.append((full_test_case_name, data_set))
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

        # get test data for each test case and append tc/data pairs to
        # execution list
        execution_list = []
        for test_case in test_case_list:
            data_sets = utils.get_test_data(workspace,
                                            project,
                                            test_case)
            for data_set in data_sets:
                execution_list.append((test_case, data_set))

    multiprocess_executor(execution_list, 1, suite_name=full_suite_name)
