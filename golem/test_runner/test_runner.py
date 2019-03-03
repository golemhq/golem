"""This module contains the method for running a single test."""
import sys
import os
import time
import traceback

from golem.core import report, utils, test_case, test_execution
from golem.test_runner.test_runner_utils import import_page_into_test_module
from golem.test_runner import execution_logger
from golem.test_runner.conf import ResultsEnum
from golem import actions, execution


class Data(dict):
    """dot notation access to dictionary attributes"""
    def __getattr__(*args):
        val = dict.get(*args)
        return Data(val) if type(val) is dict else val

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class Secrets(dict):
    """dot notation access to dictionary attributes"""
    def __getattr__(*args):
        val = dict.get(*args)
        return Secrets(val) if type(val) is dict else val

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


def run_test(workspace, project, test_name, test_data, secrets, browser,
             settings, report_directory, execution_has_failed_tests=None, tags=None):
    """Run a single test"""
    runner = TestRunner(workspace, project, test_name, test_data, secrets, browser,
                        settings, report_directory, execution_has_failed_tests, tags)
    runner.prepare()


class TestRunner:
    __test__ = False  # ignore this class from Pytest

    def __init__(self, workspace, project, test_name, test_data, secrets, browser,
                 settings, report_directory, execution_has_failed_tests=None, tags=None):
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
        self.secrets = secrets
        self.browser = browser
        self.settings = settings
        self.report_directory = report_directory
        self.test_module = None
        self.test_timestamp = utils.get_timestamp()
        self.test_start_time = time.time()
        self.logger = None
        self.execution_has_failed_tests = execution_has_failed_tests
        self.execution_tags = tags or []

    def prepare(self):
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
        execution.data = Data(self.test_data)
        execution.secrets = Secrets(self.secrets)
        execution.tags = self.execution_tags
        self._print_test_info()
        # add the 'project' directory to python path
        # to enable relative imports from the test
        # TODO
        sys.path.append(os.path.join(self.workspace, 'projects', self.project))
        self.import_modules()

    def import_modules(self):
        if '/' in self.test_name:
            self.test_name = self.test_name.replace('/', '.')
        path = test_case.generate_test_case_path(self.workspace, self.project,
                                                 self.test_name)
        test_module, error = utils.import_module(path)
        if error:
            actions._add_error(message=error.splitlines()[-1], description=error)
            self.result['result'] = ResultsEnum.CODE_ERROR
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
                    base_path = os.path.join(self.workspace, 'projects',
                                             self.project, 'pages')
                    for page in self.test_module.pages:
                        self.test_module = import_page_into_test_module(base_path,
                                                                        self.test_module,
                                                                        page.split('.'))
            except Exception as e:
                message = '{}: {}'.format(e.__class__.__name__, e)
                trcbk = traceback.format_exc()
                actions._add_error(message=message, description=trcbk)
                self.result['result'] = ResultsEnum.CODE_ERROR
        if self.result['result'] == ResultsEnum.CODE_ERROR:
            self.finalize()
        else:
            self.run_setup()

    def run_setup(self):
        try:
            if hasattr(self.test_module, 'setup'):
                self.test_module.setup(execution.data)
            else:
                execution.logger.debug('test does not have setup function')
        except AssertionError as e:
            self._add_error(message='Failure', exception=e)
            self.result['result'] = ResultsEnum.FAILURE
        except Exception as e:
            self._add_error(message='Error', exception=e)
            self.result['result'] = ResultsEnum.CODE_ERROR
        if self.result['result'] in [ResultsEnum.CODE_ERROR, ResultsEnum.FAILURE]:
            self.run_teardown()
        else:
            self.run_test()

    def run_test(self):
        try:
            if hasattr(self.test_module, 'test'):
                self.test_module.test(execution.data)
                # take screenshot_on_end
                if self.settings['screenshot_on_end'] and execution.browser:
                    actions.take_screenshot('Test end')
            else:
                error_msg = 'test {} does not have a test function'.format(self.test_name)
                actions._add_error(error_msg)
                self.result['result'] = ResultsEnum.CODE_ERROR
        except AssertionError as e:
            self._add_error(message='Failure', exception=e)
            self.result['result'] = ResultsEnum.FAILURE
        except Exception as e:
            if not self.result['result'] == ResultsEnum.FAILURE:
                self.result['result'] = ResultsEnum.CODE_ERROR
            self._add_error(message='Error', exception=e)
        self.run_teardown()

    def run_teardown(self):
        try:
            if hasattr(self.test_module, 'teardown'):
                self.test_module.teardown(execution.data)
            else:
                execution.logger.debug('test does not have a teardown function')
        except AssertionError as e:
            if not self.result['result'] == ResultsEnum.CODE_ERROR:
                self.result['result'] = ResultsEnum.FAILURE
            self._add_error(message='Failure', exception=e)
        except Exception as e:
            if not self.result['result'] == ResultsEnum.FAILURE:
                self.result['result'] = ResultsEnum.CODE_ERROR
            self._add_error(message='Error', exception=e)
        # if there is no teardown or teardown failed or it did not close the driver,
        # let's try to close the driver manually
        if execution.browser:
            try:
                for browser, driver in execution.browsers.items():
                    driver.quit()
            except:
                # if this fails, we have lost control over the webdriver window
                # and we are not going to be able to close it
                execution.logger.error('there was an error closing the driver',
                                       exc_info=True)
            finally:
                execution.browser = None
        self.finalize()

    def finalize(self):
        test_end_time = time.time()
        test_elapsed_time = round(test_end_time - self.test_start_time, 2)
        if self.result['result'] not in [ResultsEnum.CODE_ERROR, ResultsEnum.FAILURE]:
            if execution.errors:
                self.result['result'] = ResultsEnum.ERROR
            else:
                self.result['result'] = ResultsEnum.SUCCESS
        execution.logger.info('Test Result: {}'.format(self.result['result'].upper()))

        self.result['description'] = execution.description
        self.result['steps'] = execution.steps
        self.result['errors'] = execution.errors
        self.result['test_elapsed_time'] = test_elapsed_time
        self.result['test_timestamp'] = self.test_timestamp
        self.result['browser'] = execution.browser_definition['name']
        self.result['browser_full_name'] = execution.browser_definition['full_name']
        # Report a test has failed in the test execution, this will later determine the exit status
        _error_codes = [ResultsEnum.CODE_ERROR, ResultsEnum.ERROR, ResultsEnum.FAILURE]
        if self.execution_has_failed_tests is not None and self.result['result'] in _error_codes:
            self.execution_has_failed_tests.value = True
        report.generate_report(self.report_directory, self.test_name, execution.data, self.result)
        execution_logger.reset_logger(execution.logger)
        execution._reset()

    def _print_test_info(self):
        execution.logger.info('Test execution started: {}'.format(self.test_name))
        execution.logger.info('Browser: {}'.format(self.browser['name']))
        if 'env' in self.test_data:
            if 'name' in self.test_data['env']:
                execution.logger.info('Environment: {}'
                                      .format(self.test_data['env']['name']))
        if self.test_data:
            data_string = '\n'
            for key, value in self.test_data.items():
                if key == 'env':
                    if 'url' in value:
                        data_string += '    {}: {}\n'.format('url', value['url'])
                else:
                    data_string += '    {}: {}\n'.format(key, value)
            execution.logger.info('Using data:{}'.format(data_string))

    def _add_error(self, message, exception):
        """Add an error to the test from an exception.
          * Add a new step with `message`, don't log it
          * Add an error using:
              - message -> 'exception.__class__.__name__: exception'
                e.g.: 'AssertionError: expected title to be 'foo'
              - description -> traceback.format_exc()
          * Append the error to the last step
          * Log the error
          * Take a screenshot if screenshot_on_error == True and
            there is an open browser
        """
        actions._add_step(message, log_step=False)
        error_message = '{}: {}'.format(exception.__class__.__name__, exception)
        trcbk = traceback.format_exc()
        actions._add_error(message=error_message, description=trcbk)
        actions._append_error(message=error_message, description=trcbk)
        self._take_screeenshot_on_error()

    def _take_screeenshot_on_error(self):
        """Take a screenshot only if there is a browser available"""
        try:
            if self.settings['screenshot_on_error'] and execution.browser:
                actions._screenshot_on_error()
        except:
            # if the driver is not available capture screenshot is not possible
            pass
