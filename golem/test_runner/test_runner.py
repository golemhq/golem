"""
This module contains the method for running one test
"""

import importlib
import time
import traceback
import signal

import golem.core
from golem.core import report, test_execution, utils


def run_test(workspace, project, test_name, test_data, driver,
             settings, report_directory):
    ''' runs a single test case by name'''
    result = {
        'result': 'pass',
        'error': '',
        'description': '',
        'steps': [],
        'test_elapsed_time': None,
        'test_timestamp': None,
        'browser': driver
    }

    from golem.core import execution_logger
    from golem.core import actions

    # convert test_data to data obj
    # TODO convert data dict to data obj
    class data:
        pass
    new_data_class = data()
    for key, value in test_data.items():
        setattr(new_data_class, key, value)

    execution_logger.get_logger(report_directory,
                                settings['console_log_level'],
                                settings['file_log_level'],
                                settings['log_all_events'])

    execution_logger.logger.info('Test execution started: {}'.format(test_name))
    execution_logger.logger.info('Driver: {}'.format(driver))
    if test_data:
        data_string = '\n'
        for key, value in test_data.items():
            data_string += '    {}: {}\n'.format(key, value)
        execution_logger.logger.info('Using data: {}'.format(data_string))

    test_timestamp = utils.get_timestamp()
    test_start_time = time.time()

    golem.core.project = project
    golem.core.workspace = workspace
    golem.core.test_data = new_data_class
    golem.core.driver_name = driver
    golem.core.set_settings(settings)
    golem.core.report_directory = report_directory

    test_module = None
    
    try:
        test_module = importlib.import_module(
            'projects.{0}.tests.{1}'.format(project, test_name))

        # import the page objects into the test module
        if hasattr(test_module, 'pages'):
            for page in test_module.pages:
                test_module = utils.generate_page_object_module(project, test_module,
                                                                page, page.split('.'))
        
        # import logger into the test module
        setattr(test_module, 'logger', golem.core.execution_logger)
        
        # import actions into the test module
        for action in dir(golem.core.actions):
            setattr(test_module, action, getattr(golem.core.actions, action))

        # log description
        if hasattr(test_module, 'description'):
            golem.core.execution_logger.description = test_module.description
        else:
            execution_logger.logger.info('Test does not have description')
        
        # run setup method
        if hasattr(test_module, 'setup'):
            test_module.setup(golem.core.test_data)
        else:
            execution_logger.logger.info('Test does not have setup function')

        if hasattr(test_module, 'test'):
            test_module.test(golem.core.test_data)
        else:
            raise Exception('Test does not have test function')
    except:
        result['result'] = 'fail'
        result['error'] = traceback.format_exc()
        try:
            if settings['screenshot_on_error'] and golem.core.driver:
                    actions.capture('error')
        except:
            # if the test failed and driver is not available
            # capture screenshot is not possible, continue
            pass

        execution_logger.logger.error('An error ocurred:', exc_info=True)

    try:
        if hasattr(test_module, 'teardown'):
            test_module.teardown(golem.core.test_data)
        else:
            execution_logger.logger.info('Test does not have a teardown function')
    except:
        result['result'] = 'fail'
        result['error'] += '\n\nteardown failed'
        result['error'] += '\n' + traceback.format_exc()
        execution_logger.logger.error('An error ocurred in the teardown:', exc_info=True)
    
    # if there is no teardown or teardown failed or it did not close the driver,
    # let's try to close the driver manually
    if golem.core.driver:
        try:
            golem.core.driver.quit()
        except:
            # if this fails, we have lost control over the webdriver window
            # and we are not going to be able to close it
            execution_logger.logger.error('There was an error closing the driver')
            execution_logger.logger.error(traceback.format_exc())
        finally:
            golem.core.driver = None

    test_end_time = time.time()
    test_elapsed_time = round(test_end_time - test_start_time, 2)

    if not result['error']:
        execution_logger.logger.info('Test passed')

    result['description'] = execution_logger.description
    result['steps'] = execution_logger.steps
    result['test_elapsed_time'] = test_elapsed_time
    result['test_timestamp'] = test_timestamp
    result['browser'] = golem.core.get_selected_driver()

    execution_logger.description = None
    execution_logger.steps = []
    execution_logger.screenshots = {}
    report.generate_report(report_directory, test_name, golem.core.test_data, result)
    return
