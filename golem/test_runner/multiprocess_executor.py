"""
The multiprocess_executor method runs all the test cases provided in
parallel using multiprocessing.
"""
import time
from multiprocessing import Pool
from multiprocessing.pool import ApplyResult

from golem.core import test_execution
from golem.test_runner.test_runner import run_test
from golem.gui import report_parser


def multiprocess_executor(execution_list, is_suite, execution_directory, threads=1):
    print('Executing:')
    for test in execution_list:
        print('{} in {} with the following data: {}'.format(test['test_name'],
                                                            test['driver']['name'],
                                                            test['data_set']))
    start_time = time.time()

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

    # for res in lst_results:
    #    print '\none result\n',res

    pool.close()
    pool.join()

    elapsed_time = round(time.time() - start_time, 2)

    # generate execution_result.json
    report_parser.generate_execution_report(execution_directory, elapsed_time)
