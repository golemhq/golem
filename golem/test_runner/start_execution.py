"""Module that starts the execution of a suite or test."""
import sys
import traceback
import time

from golem.core import (test_execution,
                        utils,
                        report,
                        test_data,
                        environment_manager,
                        settings_manager)
from golem.core import suite as suite_module
from golem.test_runner.multiprocess_executor import multiprocess_executor
from golem.test_runner.test_runner import run_test
from golem.gui import gui_utils, report_parser


def define_drivers(drivers, remote_browsers, default_browsers):
    """Generate the definitions for the drivers.

    A defined driver contains the following attributes:
      'name':         real name
      'full_name':    remote browser name defined by user in settings
      'remote':       boolean
      'capabilities': capabilities defined by remote_browsers setting
    """
    drivers_def = []
    for driver in drivers:
        if driver in remote_browsers:
            remote_browser = remote_browsers[driver]
            _ = {
                'name': remote_browser['browserName'],
                'full_name': driver,
                'remote': True,
                'capabilities': remote_browser
            }
            drivers_def.append(_)
        elif driver in default_browsers:
            _ = {
                'name': driver,
                'full_name': None,
                'remote': False,
                'capabilities': {}
            }
            drivers_def.append(_)
        else:
            msg = ['Error: the browser {} is not defined\n'.format(driver),
                   'available options are:\n',
                   '\n'.join(default_browsers),
                   '\n'.join(remote_browsers)]
            raise Exception(''.join(msg))
    return drivers_def


def _select_environments(cli_envs, suite_envs, project_envs):
    """Define the environments to use for the test.

    The test can have a list of environments set from 2 places:
      - using the -e|--environments CLI argument
      - suite `environments` variable

    If both of these are empty try using the first env if there
    are any envs defined. Otherwise just return ['']
    meaning, no envs will be used.
    """
    envs = []
    if cli_envs:
        # use the environments passed through command line if available
        envs = cli_envs
    elif suite_envs:
        # use the environments defined in the suite
        envs = suite_envs
    elif project_envs:
        # if there are available envs, try to use the first by default
        envs = [project_envs[0]]
    else:
        # execute using a blank environment
        envs = ['']
    return envs


def _define_execution_list(workspace, project, execution):
    """Generate the execution list
    
    execution is a dictionary containing:
      'environments':   list of envs
      'tests':          list of tests
        'test_sets':    each test contains a list of test sets (data sets)
      'drivers':        list of drivers
    
    This function generates the combinations of each of the above.
    Each test should be executed once per each:
      - data set
      - environment
      - driver
    """
    execution_list = []
    test_base = settings_manager.get_project_settings(workspace, project)['base_name']
    envs_data = environment_manager.get_environment_data(workspace, project)
    for test in execution['tests']:
        if test.split(".")[-1] == test_base:
            continue
        data_sets = test_data.get_test_data(workspace, project, test)
        for data_set in data_sets:
            for env in execution['environments']:
                data_set_env = dict(data_set)
                if env in envs_data:
                    env_data = envs_data[env]
                    ## adding env_data to data_set
                    data_set_env['env'] = env_data
                    data_set_env['env']['name'] = env
                for driver in execution['drivers']:
                    execution_list.append(
                        {
                            'test_name': test,
                            'data_set': data_set_env,
                            'driver': driver,
                            'report_directory': None
                        }
                    )
    return execution_list


def _create_execution_directory(workspace, project, timestamp, test_name,
                                suite_name, is_suite):
    """Generate the execution directory."""
    execution_directory = ''
    if is_suite:
        execution_directory = report.create_execution_directory(
                                        workspace, project,
                                        timestamp, suite_name=suite_name)
    else:
        execution_directory = report.create_execution_directory(
                                        workspace, project,
                                        timestamp, test_name=test_name)
    return execution_directory


def _execute_tests():
    pass


def run_test_or_suite(workspace, project, test=None, suite=None, directory=None):
    """Run a suite or test or directory containing tests."""
    execution = {
        'tests': [],
        'workers': 1,
        'drivers': [],
        'environments': [],
        'suite_before': None,
        'suite_after': None
    }

    suite_amount_workers = None
    suite_drivers = None
    suite_envs = []
    suite_name = None
    is_suite = False

    if test:
        execution['tests'] = [test]
        suite_name = 'single_tests'
    elif suite:
        execution['tests'] = suite_module.get_suite_test_cases(workspace, project, suite)
        suite_amount_workers = suite_module.get_suite_amount_of_workers(workspace, project,
                                                                        suite)
        suite_drivers = suite_module.get_suite_browsers(workspace, project, suite)
        suite_envs = suite_module.get_suite_environments(workspace, project, suite)
        # TODO, get_before and get_after should be suite module functions
        suite_imported_module = suite_module.get_suite_module(workspace, project, suite)
        execution['suite_before'] = getattr(suite_imported_module, 'before', None)
        execution['suite_after'] = getattr(suite_imported_module, 'after', None)
        suite_name = suite
        is_suite = True
    elif directory:
        execution['tests'] = utils.get_directory_test_cases(workspace, project, directory)
        suite_name = directory
        is_suite = True
    else:
        sys.exit("ERROR: invalid arguments for run_test_or_suite()")

    # warn if no tests were found
    if len(execution['tests']) == 0:
        print('No tests were found')

    # get amount of workers (parallel executions), default is 1
    if test_execution.thread_amount > 1:
        # the thread count passed through cli has higher priority
        execution['workers'] = test_execution.thread_amount
    elif suite_amount_workers:
        execution['workers'] = suite_amount_workers

    # select the drivers to use in this execution
    # the order of precedence is:
    # 1. drivers defined by CLI
    # 2. drivers defined inside a suite
    # 3. 'default_driver' setting
    # 4. default default is 'chrome'
    settings_default_driver = test_execution.settings['default_browser']
    selected_drivers = utils.choose_driver_by_precedence(
                                cli_drivers=test_execution.cli_drivers,
                                suite_drivers=suite_drivers,
                                settings_default_driver=settings_default_driver)

    # Define the attributes for each driver
    #
    # A driver can be predefined ('chrome, 'chrome-headless', 'firefox', etc)
    # or it can be defined by the user with the 'remote_browsers' setting.
    # Remote browsers have extra details such as capabilities
    # 
    # Each driver must have the following attributes: 
    # 'name': real name,
    # 'full_name': the remote_browser name defined by the user,
    # 'remote': is this a remote_browser or not
    # 'capabilities': full capabilities defined in the remote_browsers setting
    remote_browsers = settings_manager.get_remote_browsers(test_execution.settings)
    default_browsers = gui_utils.get_supported_browsers_suggestions()
    execution['drivers'] = define_drivers(selected_drivers, remote_browsers,
                                          default_browsers)

    # Generate timestamp if needed
    # A timestamp is passed when the test is executed from the GUI.
    # The gui uses this timestamp to fetch the test execution status later on.
    # Otherwise, a new timestamp should be generated at this point
    if not test_execution.timestamp:
        test_execution.timestamp = utils.get_timestamp()

    # Select which envs to use
    # The user can define environments in the environments.json file.
    # The suite/test can be executed in one or more of these environments.
    # Which environments to use is defined by this order of preference:
    # 1. envs passed by CLI
    # 2. envs defined inside the suite
    # 3. The first env defined
    # 4. no envs at all
    #
    # Note, in the case of 4, the test might fail if it tries
    # to use env variables
    cli_envs = test_execution.cli_environments
    project_envs = environment_manager.get_envs(workspace, project)
    execution['environments'] = _select_environments(cli_envs, suite_envs, project_envs)

    # Generate the execution list
    #
    # Each test must be executed for each:
    # * data set
    # * environment
    # * driver
    #
    # The result is a list that contains all the requested combinations
    execution_list = _define_execution_list(workspace, project, execution)
    
    # create the execution directory
    #
    # if this is a suite, the directory takes this structure
    #   reports/<suite_name>/<timestamp>/
    # 
    # if this is a single test, the directory takes this structure:
    #   reports/single_tests/<test_name>/<timestamp>/
    execution_directory = _create_execution_directory(workspace, project, 
                                                      test_execution.timestamp,
                                                      test_name=test,
                                                      suite_name=suite_name,
                                                      is_suite=is_suite)
    # for each test, create the test directory
    # for example, in a suite 'suite1' with a 'test1':
    # reports/suite1/2017.07.02.19.22.20.001/test1/set_00001/
    for test in execution_list:
        report_directory = report.create_report_directory(execution_directory,
                                                          test['test_name'],
                                                          is_suite)
        test['report_directory'] = report_directory

    # EXECUTION

    start_time = time.time()
    suite_error = False

    # run suite `before` function
    if execution['suite_before']:
        try:
            execution['suite_before'].__call__()
        except:
            print('ERROR: suite before function failed')
            print(traceback.format_exc())

    if not suite_error:
        if test_execution.interactive and execution['workers'] != 1:
            print('WARNING: to run in debug mode, threads must equal one')

        if execution['workers'] == 1:
            # run tests serially
            for test in execution_list:
                run_test(workspace, project,
                         test['test_name'], test['data_set'],
                         test['driver'], test_execution.settings,
                         test['report_directory'])
        else:
            # run tests using multiprocessing
            multiprocess_executor(execution_list, execution['workers'])

    # run suite `after` function
    if execution['suite_after']:
        try:
            execution['suite_after'].__call__()
        except:
            print('ERROR: suite before function failed')
            print(traceback.format_exc())

    # generate execution_result.json
    elapsed_time = round(time.time() - start_time, 2)
    report_parser.generate_execution_report(execution_directory, elapsed_time)
