"""
The multiprocess_executor method runs all the test cases provided in
parallel using multiprocessing.
"""
import sys
import os
from multiprocessing import Pool
from multiprocessing.pool import ApplyResult

from golem.core import test_execution, utils
from golem.test_runner.test_runner import run_test


def multiprocess_executor(execution_list, processes=1):
    print('Executing:')
    for test in execution_list:
        print('{} in {} with the following data: {}'.format(test['test_name'],
                                                            test['driver'],
                                                            test['data_set']))
    # if not test_execution.timestamp:
    #     test_execution.timestamp = utils.get_timestamp()

    pool = Pool(processes=processes)

    results = []

    for test in execution_list:
        # # generate a report directory for this test
        # report_directory = report.create_report_directory(test_execution.root_path,
        #                                                   test_execution.project,
        #                                                   test['test_name'],
        #                                                   suite_name, 
        #                                                   test_execution.timestamp)

        print(test['report_directory'])

        args = (test_execution.root_path,
                test_execution.project,
                test['test_name'],
                test['data_set'],
                test['driver'],
                test_execution.settings,
                test['report_directory'])
        apply_async = pool.apply_async(run_test, args=args)
        results.append(apply_async)

    map(ApplyResult.wait, results)

    lst_results = [r.get() for r in results]

    # for res in lst_results:
    #    print '\none result\n',res

    pool.close()
    pool.join()
