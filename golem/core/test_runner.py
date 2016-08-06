import os
import sys
import traceback

from multiprocessing import Pool
from multiprocessing.pool import ApplyResult

from golem.core import utils, test_execution, logger, selenium_utils


def test_runner(project, test_case_name, suite_name, suite_data):
    ''' runs a single test case by name'''

    result = {
        'result': 'pass',
        'error': None,
        'description': None,
        'steps': None}

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

        test_data = utils.get_test_data(project, test_case_name)
        # test_data = selenium_utils.get_suite_or_test_data(
        #                     project,
        #                     test_case_name,
        #                     suite_name)
        
        if hasattr(instance, 'test'):
            instance.test(test_data)
        else:
            raise Exception
        
    except:
        result['result'] = 'fail'
        result['error'] = traceback.format_exc()
        print dir(traceback)
        print traceback.print_exc()

    if hasattr(instance, 'teardown'):
        instance.teardown()     

    result['description'] = execution_logger.description
    result['steps'] = execution_logger.steps

    return result


def multiprocess_executor(
        test_case_list=[], processes=1, suite_name=None, suite_data=None):

    pool = Pool(processes=processes) 

    results = [pool.apply_async(
                    test_runner,
                    args=(test_execution.project_name, 
                            tc, 
                            suite_name, 
                            suite_data),
                    callback=logger.log_result) 
                for tc in test_case_list]

    map(ApplyResult.wait, results)
    lst_results=[r.get() for r in results]
    print lst_results

    pool.close()
    pool.join()




def run_single_test_case(project_name, test_case_name):

    #check if test case exists and run it
    full_path = os.path.join(
                    'projects',
                    project_name,
                    'test_cases',
                    '{0}.py'.format(test_case_name))
    if not os.path.exists(full_path):
        sys.exit("ERROR: no test case named {0} exists".format(test_case_name))
    else:
        multiprocess_executor([test_case_name], 1)


def run_suite(project_name, suite_name):
    ''' a suite '''

    # TO DO implement directory suites
    
    path = os.path.join(
                'projects',
                project_name,
                'test_suites',
                '{0}.py'.format(suite_name))

    if os.path.exists(path):

        test_case_list = utils.get_suite_test_cases(project_name, suite_name)

        multiprocess_executor(test_case_list, 1, suite_name=suite_name)
