"""This module contains the method for running a single test file."""
import sys
import os
import time
import traceback

from golem.core import session
from golem.core import utils
from golem.core.test import Test
from golem.core.project import Project
from golem.test_runner.test_runner_utils import import_page_into_test
from golem.test_runner import test_logger
from golem.test_runner.conf import ResultsEnum
from golem import actions, execution
from golem.report import test_report


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


def run_test(testdir, project, test_name, test_data, secrets, browser, env_name,
             settings, exec_report_dir, set_name, test_functions=None,
             execution_has_failed_tests=None, tags=None, from_suite=False):
    """Run a single test"""
    session.testdir = testdir
    runner = TestRunner(testdir, project, test_name, test_data, secrets, browser, env_name,
                        settings, exec_report_dir, set_name, test_functions, execution_has_failed_tests,
                        tags, from_suite)
    runner.prepare()


class TestRunner:

    __test__ = False  # ignore this class from Pytest

    def __init__(self, testdir, project, test_name, test_data, secrets, browser, env_name,
                 settings, exec_report_dir, set_name, test_functions_to_run=None,
                 execution_has_failed_tests=None, tags=None, from_suite=False):
        self.testdir = testdir
        self.project = Project(project)
        self.test = Test(project, test_name)
        self.test_data = test_data
        self.secrets = secrets
        self.browser = browser
        self.env_name = env_name
        self.settings = settings
        self.exec_report_dir = exec_report_dir
        self.set_name = set_name
        # When test_functions_to_run is empty or None, all the test functions
        # defined in the test file will be run
        self.test_functions_to_run = test_functions_to_run or []
        self.test_hooks = {
            'before_test': [],
            'before_each': [],
            'after_each': [],
            'after_test': []
        }
        self.execution_has_failed_tests = execution_has_failed_tests
        self.execution_tags = tags or []
        self.from_suite = from_suite
        self.global_skip = False
        self.skip_tests = False

        self.result = None
        self.reportdir = None
        self.test_module = None
        self.test_functions = {}
        self.test_timestamp = utils.get_timestamp()
        self.logger = None

    def prepare(self):
        # Create report directory for the test file
        self.reportdir = test_report.create_test_file_report_dir(
            self.exec_report_dir, self.test.name, self.set_name)

        # Initialize logger for the test file
        self.logger = test_logger.get_logger(self.reportdir,
                                             self.settings['cli_log_level'],
                                             self.settings['log_all_events'])

        # set execution module values
        self._set_execution_module_values()
        self._print_test_info()
        # add the 'project' directory to python path
        # to enable relative imports from the test
        # TODO
        sys.path.append(os.path.join(self.testdir, 'projects', self.project.path))
        self.import_test()

    def import_test(self):
        test_module, error = utils.import_module(self.test.path)
        if error:
            actions._add_error(message=error.splitlines()[-1], description=error)
            self.result = ResultsEnum.CODE_ERROR
            self.finalize(import_modules_failed=True)
        else:
            self.test_module = test_module

            # Gather test hooks defined in the test module
            # TODO setup is deprecated, if before_test is not present, and
            #  setup is, use setup instead
            if hasattr(self.test_module, 'before_test'):
                self.test_hooks['before_test'].append(getattr(self.test_module, 'before_test'))
            elif hasattr(self.test_module, 'setup'):
                self.test_hooks['before_test'].append(getattr(self.test_module, 'setup'))

            if hasattr(self.test_module, 'before_each'):
                self.test_hooks['before_each'].append(getattr(self.test_module, 'before_each'))
            if hasattr(self.test_module, 'after_each'):
                self.test_hooks['after_each'].append(getattr(self.test_module, 'after_each'))

            # TODO teardown is deprecated, if after_test is not present, and
            #  teardown is, use teardown instead
            if hasattr(self.test_module, 'after_test'):
                self.test_hooks['after_test'].append(getattr(self.test_module, 'after_test'))
            elif hasattr(self.test_module, 'teardown'):
                self.test_hooks['after_test'].append(getattr(self.test_module, 'teardown'))

            # If test_functions_to_run is empty every test function defined in the
            # file will be run
            if not self.test_functions_to_run:
                self.test_functions_to_run = self.test.test_function_list

            if not len(self.test_functions_to_run):
                msg = f'No tests were found for file: {self.test.name}'
                execution.logger.info(msg)
                self.finalize()
                return
            else:
                for test_function in self.test_functions_to_run:
                    self.test_functions[test_function] = self._test_function_result_dict(test_function)
                self.import_modules()

    def import_modules(self):
        # import logger
        setattr(self.test_module, 'logger', execution.logger)

        # import actions module
        if self.settings['implicit_actions_import']:
            for action in utils.module_local_public_functions(actions):
                setattr(self.test_module, action, getattr(actions, action))

        # store test description
        if hasattr(self.test_module, 'description'):
            execution.description = self.test_module.description

        # import pages
        try:
            if hasattr(self.test_module, 'pages') and self.settings['implicit_page_import']:
                base_path = self.project.page_directory_path
                for page in self.test_module.pages:
                    self.test_module = import_page_into_test(base_path, self.test_module,
                                                             page.split('.'))
        except Exception as e:
            message = f'{e.__class__.__name__}: {e}'
            trcbk = traceback.format_exc()
            actions._add_error(message=message, description=trcbk)
            self.result = ResultsEnum.CODE_ERROR

        # check for skip flag
        # test is skipped only when run from a suite
        skip = getattr(self.test_module, 'skip', False)
        if skip and self.from_suite:
            self.global_skip = skip

        if self.result == ResultsEnum.CODE_ERROR:
            self.finalize(import_modules_failed=True)
        else:
            self.run_setup()

    def run_setup(self):
        if self.global_skip:
            self.run_test_functions()
            return

        for before_test_hook in self.test_hooks['before_test']:
            # TODO setup is deprecated
            # setup is still run as 'setup' and an info log is shown
            hook_name = 'before_test'
            if before_test_hook.__name__ == 'setup':
                hook_name = 'setup'
                execution.logger.info('setup hook function is deprecated, use before_test')

            # reset execution values specific to this test
            self._reset_execution_module_values_for_test_function(None, hook_name)

            result = self.generic_run_function(before_test_hook)

            if result != ResultsEnum.SUCCESS:
                self.generate_report_for_hook_function(hook_name, result)
                return self.run_teardown(setup_failed=True)

        self.run_test_functions()

    def run_test_functions(self):
        for test_function in self.test_functions:
            self.run_test_function(test_function)
        self.run_teardown()

    def run_test_function(self, test_name):
        result = self.test_functions[test_name]
        self._reset_execution_module_values_for_test_function(None, test_name)

        if self.global_skip or self.skip_tests:
            result['result'] = ResultsEnum.SKIPPED
            execution.logger.info(f'Test skipped: {test_name}')
            self._finalize_test_function(test_name)
            return

        # Create folder for the test function report
        test_reportdir = test_report.create_test_function_report_dir(self.reportdir, test_name)
        result['test_reportdir'] = test_reportdir

        # Run before_each hooks
        for before_each_hook in self.test_hooks['before_each']:
            # reset execution values specific to this test
            self._reset_execution_module_values_for_test_function(None, 'before_each')

            before_each_result = self.generic_run_function(before_each_hook)

            if before_each_result != ResultsEnum.SUCCESS:
                self.skip_tests = True
                self.generate_report_for_hook_function('before_each', before_each_result)

        # reset execution values specific to this test
        self._reset_execution_module_values_for_test_function(test_reportdir, test_name)

        if self.skip_tests:
            result['result'] = ResultsEnum.SKIPPED
            execution.logger.info(f'Test skipped: {test_name}')
            self._finalize_test_function(test_name)
            return

        execution.logger.info(f'Test started: {test_name}')

        result['start_time'] = time.time()

        try:
            f = getattr(self.test_module, test_name)
            f(execution.data)

            # take screenshot_on_end
            if self.settings['screenshot_on_end'] and execution.browser:
                actions.take_screenshot('Test end')
        except AssertionError as e:
            self._add_error(message='Failure', exception=e)
            result['result'] = ResultsEnum.FAILURE
        except Exception as e:
            result['result'] = ResultsEnum.CODE_ERROR
            self._add_error(message='Error', exception=e)

        if result['result'] not in [ResultsEnum.CODE_ERROR, ResultsEnum.FAILURE]:
            if execution.errors:
                result['result'] = ResultsEnum.ERROR

        if result['result'] in [None, ResultsEnum.PENDING]:
            result['result'] = ResultsEnum.SUCCESS

        result['end_time'] = time.time()
        result['test_elapsed_time'] = round(result['end_time'] - result['start_time'], 2)

        execution.logger.info(f"Test Result: {result['result'].upper()}")

        self._finalize_test_function(test_name)

        # Run after_each hooks
        for after_each_hook in self.test_hooks['after_each']:
            # reset execution values specific to this test
            self._reset_execution_module_values_for_test_function(None, 'after_each')

            after_each_result = self.generic_run_function(after_each_hook)

            if after_each_result != ResultsEnum.SUCCESS:
                self.skip_tests = True
                self.generate_report_for_hook_function('after_each', after_each_result)

    def _finalize_test_function(self, test_name):
        result = self.test_functions[test_name]

        result['description'] = execution.description
        result['steps'] = execution.steps
        result['errors'] = execution.errors
        result['test_timestamp'] = self.test_timestamp
        result['browser'] = execution.browser_definition['name']
        result['browser_capabilities'] = execution.browser_definition['capabilities']
        # Report a test has failed in the test execution,
        # this will later determine the exit status
        _error_codes = [ResultsEnum.CODE_ERROR, ResultsEnum.ERROR, ResultsEnum.FAILURE]
        if self.execution_has_failed_tests is not None and result['result'] in _error_codes:
            self.execution_has_failed_tests.value = True

        test_report.generate_report(self.test.name, result, execution.data, self.reportdir)

        self._reset_execution_module_values_for_test_function()

    def run_teardown(self, setup_failed=False):
        teardown_failed = False

        if self.global_skip:
            self.finalize()
            return

        for after_test_hook in self.test_hooks['after_test']:
            # TODO teardown is deprecated
            # teardown is still run as 'teardown' and an info log is shown
            hook_name = 'after_test'
            if after_test_hook.__name__ == 'teardown':
                hook_name = 'teardown'
                execution.logger.info('teardown hook function is deprecated, use after_test')

            # reset execution values specific to this test
            self._reset_execution_module_values_for_test_function(None, hook_name)

            result = self.generic_run_function(after_test_hook)

            if result != ResultsEnum.SUCCESS:
                self.generate_report_for_hook_function(hook_name, result)

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
        self.finalize(setup_failed=setup_failed, teardown_failed=teardown_failed)

    def finalize(self, import_modules_failed=False, setup_failed=False, teardown_failed=False):
        # TODO this should be called at the point it failed
        # instead of here. Use a common method to generate
        # report for test functions and not test functions, like setup, teardown.
        # Reset the execution module after each so the steps and errors
        # collected belong to each function/non function phase
        if import_modules_failed:
            result = self._test_function_result_dict('setup')
            result['result'] = self.result
            result['test_timestamp'] = self.test_timestamp
            result['errors'] = execution.errors
            test_report.generate_report(self.test.name, result, execution.data,
                                        self.reportdir)

        test_logger.reset_logger(execution.logger)

    def generic_run_function(self, function):
        result = None
        try:
            function(execution.data)
        except AssertionError as e:
            self._add_error(message='Failure', exception=e)
            result = ResultsEnum.FAILURE
        except Exception as e:
            self._add_error(message='Error', exception=e)
            result = ResultsEnum.CODE_ERROR
        if result is None:
            if execution.errors:
                result = ResultsEnum.ERROR
            else:
                result = ResultsEnum.SUCCESS
        return result

    def generate_report_for_hook_function(self, hook_name, result):
        result_dict = self._test_function_result_dict(hook_name)
        result_dict['result'] = result
        result_dict['description'] = execution.description
        result_dict['test_timestamp'] = self.test_timestamp
        result_dict['errors'] = execution.errors
        result_dict['steps'] = execution.steps
        result_dict['browser'] = execution.browser_definition['name']
        test_report.generate_report(self.test.name, result_dict, execution.data, self.reportdir)

    def _set_execution_module_values(self):
        execution.test_file = self.test.name
        execution.browser = None
        execution.browser_definition = self.browser
        execution.browsers = {}
        execution.data = Data(self.test_data)
        execution.secrets = Secrets(self.secrets)
        execution.description = None
        execution.settings = self.settings
        execution.test_dirname = self.test.dirname
        execution.test_path = self.test.path
        execution.project_name = self.project.name
        execution.project_path = self.project.path
        execution.testdir = self.testdir
        execution.execution_reportdir = self.exec_report_dir
        execution.testfile_reportdir = self.reportdir
        execution.logger = self.logger
        execution.tags = self.execution_tags
        execution.environment = self.env_name

        execution.test_name = None
        execution.steps = []
        execution.errors = []
        execution.test_reportdir = None
        execution.timers = {}

    @staticmethod
    def _reset_execution_module_values_for_test_function(test_reportdir=None, test_name=None):
        execution.test_name = test_name
        execution.steps = []
        execution.errors = []
        execution.test_reportdir = test_reportdir
        execution.timers = {}

    def _print_test_info(self):
        execution.logger.info(f'Test execution started: {self.test.name}')
        execution.logger.info(f"Browser: {self.browser['name']}")
        if 'env' in self.test_data:
            if 'name' in self.test_data['env']:
                execution.logger.info(f"Environment: {self.test_data['env']['name']}")
        if self.test_data:
            data_string = ''
            for key, value in self.test_data.items():
                if key == 'env':
                    if 'url' in value:
                        data_string += f"\n    url: {value['url']}"
                else:
                    data_string += f'\n    {key}: {value}'
            execution.logger.info(f'Using data:{data_string}')

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
        error_message = f'{exception.__class__.__name__}: {exception}'
        trcbk = traceback.format_exc().rstrip()
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

    def _test_function_result_dict(self, test_name):
        return {
            'name': test_name,
            'set_name': self.set_name,
            'start_time': None,
            'end_time': None,
            'test_reportdir': None,
            'result': ResultsEnum.PENDING,
            'errors': [],
            'description': '',
            'steps': [],
            'test_elapsed_time': None,
            'test_timestamp': None,
            'browser': '',
            'browser_capabilities': ''
        }