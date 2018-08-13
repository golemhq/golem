"""This module contains the method for running a single test."""
import sys
import os
import time
import traceback

from golem.core import report, utils, test_case
from golem.test_runner.test_runner_utils import import_page_into_test_module
from golem.test_runner import execution_logger
from golem import actions, execution
from golem.core.exceptions import TestFailure


class Data(dict):
    """dot notation access to dictionary attributes"""
    def __getattr__(*args):
        val = dict.get(*args)
        return Data(val) if type(val) is dict else val

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def _get_set_name(test_data):
    """Get the set_name from test_data
    Return the value of 'set_name' key if present in the data
    If set_name it is not present in data, return the value of the first key.
    If there's no data, leave set_name as ''
    """
    set_name = ''
    if 'set_name' in test_data:
        set_name = test_data['set_name']
    else:
        data_without_env = dict(test_data)
        data_without_env.pop('env', None)
        if data_without_env:
            set_name = test_data[next(iter(data_without_env))]
    return set_name


def _print_test_info(logger, test_name, browser, test_data):
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
        logger.info('Using data:{}'.format(data_string))


def run_test_deprecated(workspace, project, test_name, test_data, browser,
             settings, report_directory):
    """Runs a single test"""
    result = {
        'result': 'pass',
        'errors': [],
        'description': '',
        'steps': [],
        'test_elapsed_time': None,
        'test_timestamp': None,
        'browser': '',
        'browser_full_name': '',
        'set_name': '',
    }

    # from golem.test_runner import execution_logger
    # from golem import actions
    # from golem import execution

    # convert test_data to data obj
    execution.data = Data(test_data)

    # get set_name
    # set name is the value of 'set_name' if present in the data table
    # If it is not present, use the value of the first key in the data.
    # If there's no data, set_name is ''
    result['set_name'] = _get_set_name(test_data)

    logger = execution_logger.get_logger(report_directory,
                                         settings['console_log_level'],
                                         settings['log_all_events'])
    execution.logger = logger

    _print_test_info(logger, test_name, browser, test_data)

    test_timestamp = utils.get_timestamp()
    test_start_time = time.time()
    execution.project = project
    execution.workspace = workspace
    execution.browser_definition = browser
    execution.settings = settings
    execution.report_directory = report_directory

    # add the 'project' directory to python path
    # to enable relative imports from the test
    sys.path.append(os.path.join(workspace, 'projects', project))

    test_module = None


    # Import test module

    # if '/' in test_name:
    #    test_name = test_name.replace('/', '.')
    # test_module = importlib.import_module(
    #     'projects.{0}.tests.{1}'.format(project, test_name))
    path = os.path.join(workspace, 'projects', project, 'tests', test_name+'.py')
    test_module, error = utils.import_module(path)
    if error:
        result['result'] = 'error'
        result['errors'].append(error)

    if not result['errors']:
        try:
            # import each page into the test_module
            if hasattr(test_module, 'pages'):
                for page in test_module.pages:
                    test_module = import_page_into_test_module(project, test_module,
                                                               page)
        except Exception:
            raise Exception('TODO import error of page object')
            result['result'] = 'error'
            result['errors'].append(traceback.format_exc(limit=0))

    # import logger into the test module
    setattr(test_module, 'logger', execution.logger)
    # import actions into the test module
    for action in dir(actions):
        setattr(test_module, action, getattr(actions, action))
    # store test description
    if hasattr(test_module, 'description'):
        execution.description = test_module.description

    if not result['errors']:
        try:
            # run setup method
            if hasattr(test_module, 'setup'):
                test_module.setup(execution.data)
            else:
                logger.debug('Test does not have setup function')
            # run test method
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
            logger.debug('Test does not have a teardown function')
    except:
        result['result'] = 'fail'
        result['error'] += '\n\nteardown failed'
        result['error'] += '\n' + traceback.format_exc()
        logger.error('An error ocurred in the teardown:', exc_info=True)

    # if there is no teardown or teardown failed or it did not close the driver,
    # let's try to close the driver manually
    if execution.browser:
        try:
            for browser, driver in execution.browsers.items():
                driver.quit()
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

    report.generate_report(report_directory, test_name, execution.data, result)

    execution.reset()
    execution_logger.reset_logger(logger)
    return


def run_test(workspace, project, test_name, test_data, browser,
             settings, report_directory):
    """Run a single test"""
    TestRunner(workspace, project, test_name, test_data, browser,
               settings, report_directory)


class TestRunner:

    __test__ = False  # ignore this class from Pytest

    status_failure = 'failure'
    status_error = 'error'
    status_code_error = 'code error'
    status_success = 'success'

    def __init__(self, workspace, project, test_name, test_data, browser,
                 settings, report_directory):
        self.result = {
            'result': '',
            'errors': [],
            'description': '',
            'steps': [],
            'test_elapsed_time': None,
            'test_timestamp': None,
            'browser': '',
            'browser_full_name': '',
            'set_name': '',
        }
        self.workspace = workspace
        self.project = project
        self.test_name = test_name
        self.test_data = test_data
        self.browser = browser
        self.settings = settings
        self.report_directory = report_directory
        self.test_module = None
        self.test_timestamp = utils.get_timestamp()
        self.test_start_time = time.time()
        self.prepare()

    def prepare(self):
        # get set_name
        self.result['set_name'] = _get_set_name(self.test_data)
        # initialize logger
        logger = execution_logger.get_logger(self.report_directory,
                                             self.settings['console_log_level'],
                                             self.settings['log_all_events'])
        execution.logger = logger
        execution.project = self.project
        execution.workspace = self.workspace
        execution.browser_definition = self.browser
        execution.settings = self.settings
        execution.report_directory = self.report_directory
        # convert test_data to data obj
        execution.data = Data(self.test_data)

        _print_test_info(logger, self.test_name, self.browser, self.test_data)

        # add the 'project' directory to python path
        # to enable relative imports from the test
        sys.path.append(os.path.join(self.workspace, 'projects', self.project))

        self.import_modules()

    def import_modules(self):
        if '/' in self.test_name:
           self.test_name = self.test_name.replace('/', '.')
        # test_module = importlib.import_module(
        #     'projects.{0}.tests.{1}'.format(project, test_name))


        # path = os.path.join(self.workspace, 'projects', self.project, 'tests',
        #                     self.test_name + '.py')

        path = test_case.generate_test_case_path(self.workspace, self.project,
                                                 self.test_name)
        test_module, error = utils.import_module(path)
        if error:
            execution.errors.append(error)
            execution.logger.error(error)
            self.result['result'] = self.status_code_error
        else:
            self.test_module = test_module
            # import logger into the test module
            setattr(self.test_module, 'logger', execution.logger)
            # import actions into the test module
            for action in dir(actions):
                setattr(self.test_module, action, getattr(actions, action))
            # store test description
            if hasattr(self.test_module, 'description'):
                execution.description = self.test_module.description
            try:
                # import each page into the test_module
                if hasattr(self.test_module, 'pages'):
                    # for page in self.test_module.pages:
                    #     self.test_module = \
                    #         import_page_into_test_module(self.project,
                    #                                      self.test_module,
                    #                                      page)
                    base_path = os.path.join(self.workspace, 'projects',
                                             self.project, 'pages')
                    for page in self.test_module.pages:
                        self.test_module = import_page_into_test_module(base_path,
                                                                        self.test_module,
                                                                        page.split('.'))
            except Exception as e:
                error_msg = traceback.format_exc(limit=0)
                execution.errors.append(error_msg)
                execution.logger.error(error_msg)
                self.result['result'] = self.status_code_error
        if self.result['result'] == self.status_code_error:
            self.finalize()
        else:
            self.run_setup()

    def run_setup(self):
        try:
            if hasattr(self.test_module, 'setup'):
                self.test_module.setup(execution.data)
            else:
                execution.logger.debug('Test does not have setup function')
        except (AssertionError, TestFailure):
            self.result['result'] = self.status_failure
            execution.errors.append(traceback.format_exc(limit=0))
            execution.logger.error('setup failed', exc_info=True)
        except:
            self.result['result'] = self.status_code_error
            execution.errors.append(traceback.format_exc(limit=0))
            try:
                if self.settings['screenshot_on_error'] and execution.browser:
                    actions.capture('error')
            except:
                # if the test failed and driver is not available
                # capture screenshot is not possible, continue
                pass
            self._take_screeenshot_on_error(self.settings['screenshot_on_error'],
                                            execution.browser)
            execution.logger.error('setup failed', exc_info=True)

        if self.result['result'] in [self.status_code_error, self.status_failure]:
            self.run_teardown()
        else:
            self.run_test()

    def run_test(self):
        try:
            # run test method
            if hasattr(self.test_module, 'test'):
                self.test_module.test(execution.data)
            else:
                self.result['result'] = self.status_code_error
                execution.errors.append('test {} does not have a test function'
                                        .format(self.test_name))
            # if settings['screenshot_on_end'] and execution.browser:
            #    actions.capture('test end')
        except AssertionError:
            self.result['result'] = self.status_failure
            execution.errors.append(traceback.format_exc(limit=0))
            self._take_screeenshot_on_error(self.settings['screenshot_on_error'],
                                               execution.browser)
            execution.logger.error('An error ocurred:', exc_info=True)
        except:
            if not self.result['result'] == self.status_failure:
                self.result['result'] = self.status_code_error
            execution.errors.append(traceback.format_exc(limit=0))
            self._take_screeenshot_on_error(self.settings['screenshot_on_error'],
                                               execution.browser)
            execution.logger.error('An error ocurred:', exc_info=True)
        self.run_teardown()

    def run_teardown(self):
        try:
            if hasattr(self.test_module, 'teardown'):
                self.test_module.teardown(execution.data)
            else:
                execution.logger.debug('Test does not have a teardown function')
        except AssertionError:
            self.result['result'] = self.status_failure
            execution.errors.append(traceback.format_exc(limit=0))
            self._take_screeenshot_on_error(self.settings['screenshot_on_error'],
                                            execution.browser)
            execution.logger.error('An error ocurred:', exc_info=True)
        except:
            if not self.result['result'] == self.status_failure:
                self.result['result'] = self.status_code_error
            execution.errors.append(traceback.format_exc(limit=0))
            self._take_screeenshot_on_error(self.settings['screenshot_on_error'],
                                               execution.browser)
            execution.logger.error('An error ocurred:', exc_info=True)
            # self.result['result'] = 'fail'
            # self.result['error'] += '\n\nteardown failed'
            # self.result['error'] += '\n' + traceback.format_exc()
            # self.logger.error('An error ocurred in the teardown:', exc_info=True)

        # if there is no teardown or teardown failed or it did not close the driver,
        # let's try to close the driver manually
        if execution.browser:
            try:
                for browser, driver in execution.browsers.items():
                    driver.quit()
            except:
                # if this fails, we have lost control over the webdriver window
                # and we are not going to be able to close it
                execution.logger.error('There was an error closing the driver')
                execution.logger.error(traceback.format_exc())
            finally:
                execution.browser = None

        self.finalize()

    def finalize(self):
        test_end_time = time.time()
        test_elapsed_time = round(test_end_time - self.test_start_time, 2)

        if self.result['result'] not in [self.status_code_error, self.status_failure]:
            if execution.errors:
                self.result['result'] = self.status_error
            else:
                self.result['result'] = self.status_success

        # if not self.result['errors']:
        #     self.logger.info('Test passed')

        execution.logger.info('Test end: {}'.format(self.result['result']))

        self.result['description'] = execution.description
        self.result['steps'] = execution.steps
        self.result['errors'] = execution.errors
        self.result['test_elapsed_time'] = test_elapsed_time
        self.result['test_timestamp'] = self.test_timestamp
        self.result['browser'] = execution.browser_definition['name']
        self.result['browser_full_name'] = execution.browser_definition['full_name']

        report.generate_report(self.report_directory, self.test_name, execution.data, self.result)

        execution_logger.reset_logger(execution.logger)
        execution._reset()

    def _take_screeenshot_on_error(self, screenshot_on_error, browser):
        try:
            if screenshot_on_error and browser:
                actions.capture('error')
        except:
            # if the driver is not available capture screenshot is not possible
            pass


