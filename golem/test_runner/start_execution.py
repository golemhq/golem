"""
"""
import sys

from golem.core import (test_execution,
                        utils,
                        report,
                        test_data,
                        environment_manager,
                        settings_manager)
from golem.test_runner.multiprocess_executor import multiprocess_executor, run_test
from golem.gui import gui_utils


def run_test_or_suite(workspace, project, test=None, suite=None, directory_suite=None):
    '''run a test, a suite or a "directory suite"'''
    # suitex = {
    #     'tests': []
    # }
    tests = []
    threads = 1
    suite_amount_workers = None
    suite_drivers = None
    suite_envs = []
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
        suite_envs = utils.get_suite_environments(workspace, project, suite)
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
    
    # check if drivers are remote
    remote_browsers = settings_manager.get_remote_browsers(test_execution.settings)
    default_browsers = gui_utils.get_supported_browsers_suggestions()
    drivers_temp = []
    for driver in drivers:
        if driver in remote_browsers:
            remote_browser = test_execution.settings['remote_browsers'][driver]
            _ = {
                'name': remote_browser['browserName'],
                'full_name': driver,
                'remote': True,
                'capabilities': remote_browser
            }
            drivers_temp.append(_)
        elif driver in default_browsers:
            _ = {
                'name': driver,
                'full_name': '',
                'remote': False,
                'capabilities': None
            }
            drivers_temp.append(_)
        else:
            msg = ['Error: the browser {} is not defined\n'.format(driver),
                   'available options are:\n',
                   '\n'.join(default_browsers),
                   '\n'.join(remote_browsers)]
            #sys.exit('Error: the browser {} is not defined'.format(driver))
            sys.exit(''.join(msg))

    drivers = drivers_temp

    # timestamp is passed when the test is executed from the GUI,
    # otherwise, a timestamp should be generated at this point
    # the timestamp is used to identify this unique execution of the test or suite
    if not test_execution.timestamp:
        test_execution.timestamp = utils.get_timestamp()

    #######
    project_envs = environment_manager.get_envs(project)
    envs = []
    if test_execution.cli_environments:
        # use the environments passed through command line if available
        envs = test_execution.cli_environments
    elif suite_envs:
        # use the environments defined in the suite
        envs = suite_envs
    elif project_envs:
        # if there are available envs, try to use the first by default
        envs = [project_envs[0]]
    else:
        # execute using a blank environment
        envs = ['']

    envs_data = environment_manager.get_environment_data(project)
    # get test data for each test present in the list of tests
    # for each test in the list, for each data set and driver combination
    # append an entry to the execution_list
    execution_list = []
    for test_case in tests:
        data_sets = test_data.get_test_data(workspace, project, test_case)
        for data_set in data_sets:
            for env in envs:
                data_set_env = dict(data_set)
                if env in envs_data:
                    env_data = envs_data[env]
                    ## adding env_data to data_set
                    data_set_env['env'] = env_data
                    data_set_env['env']['name'] = env
                for driver in drivers:
                    execution_list.append(
                        {
                            'test_name': test_case,
                            'data_set': data_set_env,
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
        # run list of tests using multiprocessing
        multiprocess_executor(execution_list, is_suite, execution_directory, threads)

    if suite:
        if hasattr(suite_module, 'after'):
            suite_module.after()
