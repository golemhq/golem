import os
import sys
import traceback
import time
import multiprocessing
from types import SimpleNamespace
from collections import OrderedDict

from golem.core import (test_execution,
                        utils,
                        report,
                        test_data,
                        environment_manager,
                        settings_manager,
                        secrets_manager)
from golem.core import suite as suite_module
from golem.gui import gui_utils, report_parser
from golem.test_runner.multiprocess_executor import multiprocess_executor
from golem.test_runner.test_runner import run_test


def define_browsers(browsers, remote_browsers, default_browsers):
    """Generate the definitions for the browsers.

    A defined browser contains the following attributes:
      'name':         real name
      'full_name':    remote browser name defined by user in settings
      'remote':       boolean
      'capabilities': capabilities defined by remote_browsers setting
    """
    browsers_definition = []
    for browser in browsers:
        if browser in remote_browsers:
            remote_browser = remote_browsers[browser]
            b = {
                'name': remote_browser['browserName'],
                'full_name': browser,
                'remote': True,
                'capabilities': remote_browser
            }
            browsers_definition.append(b)
        elif browser in default_browsers:
            b = {
                'name': browser,
                'full_name': None,
                'remote': False,
                'capabilities': {}
            }
            browsers_definition.append(b)
        else:
            msg = ['Error: the browser {} is not defined\n'.format(browser),
                   'available options are:\n',
                   '\n'.join(default_browsers),
                   '\n'.join(remote_browsers)]
            raise Exception(''.join(msg))
    return browsers_definition


class ExecutionRunner:
    """Executes tests or suites.

    Three points of entry:
      run_test
      run_suite
      run_directory
    """

    def __init__(self, browsers=None, processes=1, environments=None, interactive=False,
                 timestamp=None, reports=None, report_folder=None, report_name=None):
        if reports is None:
            reports = []
        self.project = None
        self.cli_args = SimpleNamespace(browsers=browsers, processes=processes,
                                        envs=environments)
        self.interactive = interactive
        self.timestamp = timestamp
        self.reports = reports
        self.report_folder = report_folder
        self.report_name = report_name
        self.report = {}
        self.tests = []
        self.is_suite = False
        self.suite_name = None
        self.test_name = None
        self.selected_browsers = None
        self.start_time = None
        self.suite = SimpleNamespace(processes=None, browsers=None, envs=None,
                                     before=None, after=None)
        has_failed_tests = self._create_execution_has_failed_tests_flag()
        self.execution = SimpleNamespace(processes=1, browsers=[], envs=[],
                                         tests=[], reportdir=None,
                                         has_failed_tests=has_failed_tests)

    @staticmethod
    def _create_execution_has_failed_tests_flag():
        """Multiprocessing safe flag to track if any test has failed or
        errored during the execution

        Returns a multiprocessing.managers.ValueProxy
        """
        return multiprocessing.Manager().Value('error', False)

    def _select_environments(self):
        """Define the environments to use for the test.

        The test can have a list of environments set from 2 places:
          - using the -e|--environments CLI argument
          - suite `environments` variable

        If both of these are empty try using the first env if there
        are any envs defined for the project. Otherwise just return ['']
        meaning: no envs will be used.
        """
        all_project_envs = environment_manager.get_envs(test_execution.root_path,
                                                        self.project)
        if self.cli_args.envs:
            # use the environments passed through command line
            envs = self.cli_args.envs
        elif self.suite.envs:
            # use the environments defined in the suite
            envs = self.suite.envs
        elif all_project_envs:
            # if there are available envs, use the first by default
            envs = [sorted(all_project_envs)[0]]
        else:
            envs = ['']
        return envs

    def _create_execution_directory(self):
        """Generate the execution report directory"""
        if self.is_suite:
            execution_directory = report.create_execution_directory(
                test_execution.root_path, self.project,
                self.timestamp, suite_name=self.suite_name)
        else:
            execution_directory = report.create_execution_directory(
                test_execution.root_path, self.project,
                self.timestamp, test_name=self.test_name)
        return execution_directory

    def _define_execution_list(self):
        """Generate the execution list

        Generates a list with the required combinations
        for each of the following elements:
          - tests
          - data sets
          - environments
          - browsers
        """
        execution_list = []
        testdir = test_execution.root_path
        envs_data = environment_manager.get_environment_data(testdir, self.project)
        secrets = secrets_manager.get_secrets(testdir, self.project)
        for test in self.tests:
            data_sets = test_data.get_test_data(testdir, self.project, test)
            for data_set in data_sets:
                for env in self.execution.envs:
                    data_set_env = dict(data_set)
                    if env in envs_data:
                        # add env_data to data_set
                        data_set_env['env'] = envs_data[env]
                        data_set_env['env']['name'] = env
                    for browser in self.execution.browsers:
                        testdef = SimpleNamespace(name=test, data_set=data_set_env, secrets=secrets,
                                                  browser=browser, reportdir=None)
                        execution_list.append(testdef)
        return execution_list

    def _print_number_of_tests_found(self):
        """Print number of tests and test sets to console"""
        test_number = len(self.tests)
        set_number = len(self.execution.tests)
        if test_number > 1 or set_number > 1:
            msg = 'Tests found: {}'.format(test_number)
            if test_number != set_number:
                msg = '{} ({} sets)'.format(msg, set_number)
            print(msg)

    def _print_results(self):
        result_string = ''
        for result, number in OrderedDict(self.report['totals_by_result']).items():
            result_string += ' {} {},'.format(number, result)
        elapsed_time = self.report['net_elapsed_time']
        if elapsed_time > 60:
            in_elapsed_time = ' in {} minutes'.format(round(elapsed_time / 60, 2))
        else:
            in_elapsed_time = ' in {} seconds'.format(elapsed_time)
        output = 'Result:{}{}'.format(result_string[:-1], in_elapsed_time)
        print()
        print(output)

    def _get_elapsed_time(self, start_time):
        elapsed_time = 0
        if start_time:
            elapsed_time = round(time.time() - self.start_time, 2)
        return elapsed_time

    def run_test(self, test):
        """Run a single test.
        `test` can be a path to a Python file or an import path.
        Both relative to the tests folder.
        Example:
            test = 'folder/test.py'
            test = 'folder.test'
        """
        if test.endswith('.py'):
            filename, _ = os.path.splitext(test)
            test = '.'.join(os.path.normpath(filename).split(os.sep))
        self.tests = [test]
        self.test_name = test
        self.suite_name = 'single_tests'
        self._prepare()

    def run_suite(self, suite):
        """Run a suite.
        `suite` can be a path to a Python file or an import path.
        Both relative to the suites folder.
        Example:
            test = 'folder/suite.py'
            test = 'folder.suite'
        """
        # TODO
        if suite.endswith('.py'):
            filename, _ = os.path.splitext(suite)
            suite = '.'.join(os.path.normpath(filename).split(os.sep))
        self.tests = suite_module.get_suite_test_cases(test_execution.root_path,
                                                       self.project, suite)
        if len(self.tests) == 0:
            sys.exit('No tests were found for suite {}'.format(suite))
        suite_amount_workers = suite_module.get_suite_amount_of_workers(
            test_execution.root_path, self.project, suite)
        self.suite.processes = suite_amount_workers
        self.suite.browsers = suite_module.get_suite_browsers(test_execution.root_path,
                                                              self.project, suite)
        self.suite.envs = suite_module.get_suite_environments(test_execution.root_path,
                                                              self.project, suite)
        suite_imported_module = suite_module.get_suite_module(test_execution.root_path,
                                                              self.project, suite)
        self.suite.before = getattr(suite_imported_module, 'before', None)
        self.suite.after = getattr(suite_imported_module, 'after', None)
        self.suite_name = suite
        self.is_suite = True
        self._prepare()

    def run_directory(self, directory):
        """Run every test inside a directory.
        `directory` has to be a relative path from the tests folder.
        To run every test in tests folder use: directory=''
        """
        self.tests = utils.get_directory_tests(test_execution.root_path,
                                               self.project, directory)
        if len(self.tests) == 0:
            sys.exit('No tests were found in {}'.format(os.path.join('tests', directory)))
        self.is_suite = True
        if directory == '':
            suite_name = 'all'
        else:
            suite_name = '.'.join(os.path.normpath(directory).split(os.sep))
        self.suite_name = suite_name
        self._prepare()

    def _prepare(self):
        # Generate timestamp if needed.
        # A timestamp is passed when the test is executed from the GUI.
        # The gui uses this timestamp to fetch the test execution status later on.
        # Otherwise, a new timestamp should be generated at this point.
        if not self.timestamp:
            self.timestamp = utils.get_timestamp()

        # get amount of processes (parallel executions), default is 1
        if self.cli_args.processes > 1:
            # the processes arg passed through cli has higher priority
            self.execution.processes = self.cli_args.processes
        elif self.suite.processes:
            self.execution.processes = self.suite.processes

        # select the browsers to use in this execution
        # the order of precedence is:
        # 1. browsers defined by CLI
        # 2. browsers defined inside a suite
        # 3. 'default_browser' setting key
        # 4. default default is 'chrome'
        self.selected_browsers = utils.choose_browser_by_precedence(
            cli_browsers=self.cli_args.browsers,
            suite_browsers=self.suite.browsers,
            settings_default_browser=test_execution.settings['default_browser'])

        # Define the attributes for each browser.
        # A browser name can be predefined ('chrome, 'chrome-headless', 'firefox', etc)
        # or it can be defined by the user with the 'remote_browsers' setting.
        # Remote browsers have extra details such as capabilities
        #
        # Each defined browser must have the following attributes:
        # 'name': real name,
        # 'full_name': the remote_browser name defined by the user,
        # 'remote': is this a remote_browser or not
        # 'capabilities': full capabilities defined in the remote_browsers setting
        remote_browsers = settings_manager.get_remote_browsers(test_execution.settings)
        default_browsers = gui_utils.get_supported_browsers_suggestions()
        self.execution.browsers = define_browsers(self.selected_browsers, remote_browsers,
                                                  default_browsers)
        # Select which environments to use
        # The user can define environments in the environments.json file.
        # The suite/test can be executed in one or more of these environments.
        # Which environments will be used is defined by this order of preference:
        # 1. envs passed by CLI
        # 2. envs defined inside the suite
        # 3. The first env defined for the project
        # 4. no envs at all
        #
        # Note, in the case of 4, the test might fail if it tries
        # to use env variables
        self.execution.envs = self._select_environments()

        # create the execution report directory
        # if this is a suite, the directory takes this structure:
        #   reports/<suite_name>/<timestamp>/
        #
        # if this is a single test, the directory takes this structure:
        #   reports/single_tests/<test_name>/<timestamp>/
        self.execution.reportdir = self._create_execution_directory()

        # Generate the execution list
        # Each test must be executed for each:
        # * data set
        # * environment
        # * browser
        # The result is a list that contains all the requested combinations
        self.execution.tests = self._define_execution_list()

        self._print_number_of_tests_found()

        # for each test, create the test report directory
        # for example, in a suite 'suite1' with a 'test1':
        # reports/suite1/2017.07.02.19.22.20.001/test1/set_00001/
        for test in self.execution.tests:
            test.reportdir = report.create_report_directory(self.execution.reportdir,
                                                            test.name, self.is_suite)
        try:
            self._execute()
        except KeyboardInterrupt:
            self.execution.has_failed_tests.value = True
            self._finalize()

    def _execute(self):
        self.start_time = time.time()
        suite_error = False

        # run suite `before` function
        if self.suite.before:
            try:
                self.suite.before.__call__()
            except:
                print('ERROR: suite before function failed')
                print(traceback.format_exc())

        if not suite_error:
            if self.interactive and self.execution.processes != 1:
                print('WARNING: to run in debug mode, threads must equal one')

            if self.execution.processes == 1:
                # run tests serially
                for test in self.execution.tests:
                    run_test(test_execution.root_path, self.project, test.name,
                             test.data_set, test.secrets, test.browser,
                             test_execution.settings, test.reportdir,
                             self.execution.has_failed_tests)
            else:
                # run tests using multiprocessing
                multiprocess_executor(self.project, self.execution.tests,
                                      self.execution.has_failed_tests,
                                      self.execution.processes)

        # run suite `after` function
        if self.suite.after:
            try:
                self.suite.after.__call__()
            except:
                print('ERROR: suite before function failed')
                print(traceback.format_exc())

        self._finalize()

    def _finalize(self):
        elapsed_time = self._get_elapsed_time(self.start_time)

        # generate report.json
        self.report = report_parser.generate_execution_report(self.execution.reportdir,
                                                              elapsed_time)

        if self.is_suite:
            self._print_results()

        # generate requested reports
        if self.is_suite:
            report_name = self.report_name or 'report'
            report_folder = self.report_folder or self.execution.reportdir
            if 'junit' in self.reports:
                report_parser.generate_junit_report(self.execution.reportdir,
                                                    self.suite_name, self.timestamp,
                                                    self.report_folder, report_name)
            if 'json' in self.reports and (self.report_folder or self.report_name):
                report_parser.save_execution_json_report(self.report, report_folder, report_name)
            if 'html' in self.reports:
                gui_utils.generate_html_report(self.project, self.suite_name,
                                               self.timestamp, self.report_folder,
                                               report_name)
            if 'html-no-images' in self.reports:
                if 'html' in self.reports:
                    report_name = report_name + '-no-images'
                gui_utils.generate_html_report(self.project, self.suite_name, self.timestamp,
                                               self.report_folder, report_name,
                                               no_images=True)

        # exit to the console with exit status code 1 in case a test fails
        if self.execution.has_failed_tests.value:
            sys.exit(1)
