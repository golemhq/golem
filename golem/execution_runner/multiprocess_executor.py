"""The multiprocess_executor method runs all the test cases
provided in parallel using multiprocessing.
"""
from multiprocessing import Pool
from multiprocessing.pool import ApplyResult

from golem.core import session
from golem.test_runner.test_runner import run_test


def multiprocess_executor(project, execution_list, has_failed_tests, processes=1,
                          tags=None, is_suite=False):
    """Runs a list of tests in parallel using multiprocessing"""
    pool = Pool(processes=processes, maxtasksperchild=1)
    results = []
    for test in execution_list:
        args = (session.testdir,
                project,
                test.name,
                test.data_set,
                test.secrets,
                test.browser,
                test.env,
                session.settings,
                test.reportdir,
                has_failed_tests,
                tags,
                is_suite)
        apply_async = pool.apply_async(run_test, args=args)
        results.append(apply_async)
    map(ApplyResult.wait, results)
    pool.close()
    pool.join()
