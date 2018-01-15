"""The multiprocess_executor method runs all the test cases
provided in parallel using multiprocessing.
"""
import time
from multiprocessing import Pool
from multiprocessing.pool import ApplyResult

from golem.core import test_execution
from golem.test_runner.test_runner import run_test


def multiprocess_executor(execution_list, threads=1):
    """Runs a list of tests in parallel using multiprocessing.

    execution_list is a list of dictionaries, each containing:
      'test_name',
      'data_set',
      'driver',
      'report_directory'
    """
    print('Executing:')
    for test in execution_list:
        print('{} in {} with the following data: {}'.format(test['test_name'],
                                                            test['driver']['name'],
                                                            test['data_set']))
    # TODO test that a worker is used once and then replaced
    pool = Pool(processes=threads, maxtasksperchild=1)
    results = []
    for test in execution_list:
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
    pool.close()
    pool.join()
