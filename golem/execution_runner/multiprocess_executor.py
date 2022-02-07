"""The multiprocess_executor method runs all the test cases
provided in parallel using multiprocessing.
"""
from multiprocessing import Pool
from multiprocessing.pool import ApplyResult

from golem.core import test_execution
from golem.test_runner.test_runner import run_test


def multiprocess_executor(project, execution_list, has_failed_tests, processes=1):
    """Runs a list of tests in parallel using multiprocessing"""
    pool = Pool(processes=processes, maxtasksperchild=1)
    results = []
    try:
        for test in execution_list:
            args = (test_execution.root_path,
                    project,
                    test.name,
                    test.data_set,
                    test.secrets,
                    test.browser,
                    test_execution.settings,
                    test.reportdir,
                    has_failed_tests)
            apply_async = pool.apply_async(run_test, args=args)
            results.append(apply_async)
        map(ApplyResult.wait, results)
        pool.close()
        pool.join()
    except KeyboardInterrupt:
        print("KeyboardInterrupt detected, ending test run.")
        pool.terminate()
        pool.join()
