"""
This module contains the method for running one test (one execution)
i.e.: one test with a single test set
"""
import sys
import os
import importlib
import time
import traceback

from golem.core import report, utils


def run_test(workspace, project, test_name, test_data, browser,
             settings, report_directory):
    ''' runs a single test case by name'''
    result = {
        'result': 'pass',
        'error': '',
        'description': '',
        'steps': [],
        'test_elapsed_time': None,
        'test_timestamp': None,
        'browser': '',
        'browser_full_name': '',
        'set_name': '',
    }

    from golem.core import execution_logger
    from golem import actions
    from golem import execution

    # convert test_data to data obj
    class Data(dict):
        """dot notation access to dictionary attributes"""
        def __getattr__(*args):
            val = dict.get(*args)
            return Data(val) if type(val) is dict else val

        __setattr__ = dict.__setitem__
        __delattr__ = dict.__delitem__

    execution.data = Data(test_data)

    # set set_name
    # set name is the value of 'set_name' if present in the data table
    # if it is not present, use the value of the first column in the data table
    # if there's no data in the data table, leave set_name as ''
    if 'set_name' in test_data:
        result['set_name'] = test_data['set_name']
    elif test_data:
        result['set_name'] = test_data[next(iter(test_data))]

    logger = execution_logger.get_logger(report_directory,
                                         settings['console_log_level'],
                                         settings['file_log_level'],
                                         settings['log_all_events'])
    execution.logger = logger

    # Print execution info to console
    logger.info('Test execution started: {}'.format(test_name))
    logger.info('Browser: {}'.format(browser['name']))
    if 'env' in test_data:
        if 'name' in test_data['env']:
            logger.info('Environment: {}'.format(test_data['env']['name']))
    if test_data:
        data_string = '\n'
        for key, value in test_data.items():
            if key == 'env':
                if 'url' in value:
                    data_string += '    {}: {}\n'.format('url', value['url'])
            else:
                data_string += '    {}: {}\n'.format(key, value)
        logger.info('Using data: {}'.format(data_string))

    test_timestamp = utils.get_timestamp()
    test_start_time = time.time()
    execution.project = project
    execution.workspace = workspace
    execution.browser_definition = browser
    execution.settings = settings
    execution.report_directory = report_directory

    # add the 'project' directory to python path
    # so it's possible to make relative imports from the test
    # example, some_test.py
    # from pages import some_page
    sys.path.append(os.path.join(workspace, 'projects', project))

    test_module = None

    try:
        if '/' in test_name:
            test_name = test_name.replace('/', '.')
        test_module = importlib.import_module(
            'projects.{0}.tests.{1}'.format(project, test_name))

        # import the page objects into the test module
        if hasattr(test_module, 'pages'):
            for page in test_module.pages:
                test_module = utils.generate_page_object_module(project, test_module,
                                                                page, page.split('.'))

        # import logger into the test module
        setattr(test_module, 'logger', execution.logger)

        # import actions into the test module
        for action in dir(actions):
            setattr(test_module, action, getattr(actions, action))

        # log description
        if hasattr(test_module, 'description'):
            execution.description = test_module.description
        else:
            logger.info('Test does not have description')

        # run setup method
        if hasattr(test_module, 'setup'):
            test_module.setup(execution.data)
        else:
            logger.info('Test does not have setup function')

        if hasattr(test_module, 'test'):
            test_module.test(execution.data)
        else:
            raise Exception('Test does not have test function')

        if settings['screenshot_on_end'] and execution.browser:
            actions.capture('test end')
    except:
        result['result'] = 'fail'
        result['error'] = traceback.format_exc()
        try:
            if settings['screenshot_on_error'] and execution.browser:
                actions.capture('error')
        except:
            # if the test failed and driver is not available
            # capture screenshot is not possible, continue
            pass

        logger.error('An error ocurred:', exc_info=True)

    try:
        if hasattr(test_module, 'teardown'):
            test_module.teardown(execution.data)
        else:
            logger.info('Test does not have a teardown function')
    except:
        result['result'] = 'fail'
        result['error'] += '\n\nteardown failed'
        result['error'] += '\n' + traceback.format_exc()
        logger.error('An error ocurred in the teardown:', exc_info=True)

    # if there is no teardown or teardown failed or it did not close the driver,
    # let's try to close the driver manually
    if execution.browser:
        try:
            execution.browser.quit()
        except:
            # if this fails, we have lost control over the webdriver window
            # and we are not going to be able to close it
            logger.error('There was an error closing the driver')
            logger.error(traceback.format_exc())
        finally:
            execution.browser = None

    test_end_time = time.time()
    test_elapsed_time = round(test_end_time - test_start_time, 2)

    if not result['error']:
        logger.info('Test passed')

    result['description'] = execution.description
    result['steps'] = execution.steps
    result['test_elapsed_time'] = test_elapsed_time
    result['test_timestamp'] = test_timestamp
    result['browser'] = execution.browser_definition['name']
    result['browser_full_name'] = execution.browser_definition['full_name']

    # remove golem.execution from sys.modules to guarantee thread safety
    #sys.modules['golem.execution'] = None
    
    report.generate_report(report_directory, test_name, execution.data, result)
    del execution
    return
