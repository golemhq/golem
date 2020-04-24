import os
import sys
import traceback
import time
import multiprocessing
from types import SimpleNamespace
from collections import OrderedDict

from golem.core import (session,
                        utils,
                        test_data,
                        environment_manager,
                        settings_manager,
                        secrets_manager,)
from golem.core import suite as suite_module
from golem.core import tags_manager
from golem.core.project import Project
from golem.gui import gui_utils
from golem.test_runner.multiprocess_executor import multiprocess_executor
from golem.test_runner.test_runner import run_test
from golem.report import execution_report as exec_report
from golem.report import test_report
from golem.report import junit_report
from golem.report import html_report


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
                 timestamp=None, reports=None, report_folder=None, report_name=None, tags=None):
        if reports is None:
            reports = []
        if tags is None:
            tags = []
        self.project = None
        self.cli_args = SimpleNamespace(browsers=browsers, processes=processes,
                                        envs=environments, tags=tags)
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
                                     before=None, after=None, tags=None)
        has_failed_tests = self._create_execution_has_failed_tests_flag()
        self.execution = SimpleNamespace(processes=1, browsers=[], envs=[],
                                         tests=[], reportdir=None, tags=[],
                                         has_failed_tests=has_failed_tests)

    @staticmethod
    def _create_execution_has_failed_tests_flag():
        """Multiprocessing safe flag to track if any test has failed or
        errored during the execution

        Returns a multiprocessing.managers.ValueProxy
        """
        return multiprocessing.Manager().Value('error', False)

    def _select_environments(self, project_envs):
        """Define the environments to use for the test.

        The test can have a list of environments set from 2 places:
          - using the -e|--environments CLI argument
          - suite `environments` variable

        If both of these are empty try using the first env if there
        are any envs defined for the project. Otherwise just return ['']
        meaning: no envs will be used.
        """
        if self.cli_args.envs:
            # use the environments passed through command line
            envs = self.cli_args.envs
        elif self.suite.envs:
            # use the environments defined in the suite
            envs = self.suite.envs
        elif project_envs:
            # if there are available envs, use the first by default
            envs = [sorted(project_envs)[0]]
        else:
            envs = []
        return envs

    def _create_execution_directory(self):
        """Generate the execution report directory"""
        if self.is_suite:
            directory = exec_report.create_execution_directory(
                self.project, self.suite_name, self.timestamp)
        else:
            directory = exec_report.create_execution_dir_single_test(
                self.project, self.test_name, self.timestamp)
        return directory

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
        envs = self.execution.envs or [None]
        envs_data = environment_manager.get_environment_data(self.project)
        secrets = secrets_manager.get_secrets(self.project)

        for test in self.tests:
            data_sets = test_data.get_test_data(self.project, test)
            for data_set in data_sets:
                for env in envs:
                    data_set_env = dict(data_set)
                    if env in envs_data:
                        # add env_data to data_set
                        data_set_env['env'] = envs_data[env]
                        data_set_env['env']['name'] = env
                    for browser in self.execution.browsers:
                        testdef = SimpleNamespace(name=test, data_set=data_set_env, secrets=secrets,
                                                  browser=browser, reportdir=None, env=env)
                        execution_list.append(testdef)
        return execution_list

    def _print_number_of_tests_found(self):
        """Print number of tests and test sets to console"""
        test_number = len(self.tests)
        set_number = len(self.execution.tests)
        if test_number > 0:
            msg = 'Tests found: {}'.format(test_number)
            if test_number != set_number:
                msg = '{} ({} sets)'.format(msg, set_number)
            print(msg)

    def _filter_tests_by_tags(self):
        tests = []
        try:
            tests = tags_manager.filter_tests_by_tags(self.project, self.tests,
                                                      self.execution.tags)
        except tags_manager.InvalidTagExpression as e:
            print('{}: {}'.format(e.__class__.__name__, e))
            self.execution.has_failed_tests.value = True
        else:
            if len(tests) == 0:
                print("No tests found with tag(s): {}".format(', '.join(self.execution.tags)))
        return tests

    def _print_results(self):
        if self.report['total_tests'] > 0:
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

        suite_obj = suite_module.Suite(self.project, suite)

        self.tests = suite_obj.tests
        if len(self.tests) == 0:
            print('No tests found for suite {}'.format(suite))

        self.suite.processes = suite_obj.processes
        self.suite.browsers = suite_obj.browsers
        self.suite.envs = suite_obj.environments
        self.suite.tags = suite_obj.tags
        module = suite_obj.get_module()
        self.suite.before = getattr(module, 'before', None)
        self.suite.after = getattr(module, 'after', None)
        self.suite_name = suite
        self.is_suite = True
        self._prepare()

    def run_directory(self, directory):
        """Run every test inside a directory.
        `directory` has to be a relative path from the tests folder.
        To run every test in tests folder use: directory=''
        """
        self.tests = Project(self.project).tests(directory=directory)
        if len(self.tests) == 0:
            print('No tests were found in {}'.format(os.path.join('tests', directory)))
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

        # create the execution report directory
        # if this is a suite, the directory takes this structure:
        #   reports/<suite_name>/<timestamp>/
        #
        # if this is a single test, the directory takes this structure:
        #   reports/single_tests/<test_name>/<timestamp>/
        self.execution.reportdir = self._create_execution_directory()

        # Filter tests by tags
        self.execution.tags = self.cli_args.tags or self.suite.tags or []
        if self.execution.tags:
            self.tests = self._filter_tests_by_tags()

        if not self.tests:
            self._finalize()
        else:
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
                settings_default_browser=session.settings['default_browser'])

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
            remote_browsers = settings_manager.get_remote_browsers(session.settings)
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
            project_envs = environment_manager.get_envs(self.project)
            self.execution.envs = self._select_environments(project_envs)
            invalid_envs = [e for e in self.execution.envs if e not in project_envs]
            if invalid_envs:
                print('ERROR: the following environments do not exist for project {}: {}'
                      .format(self.project, ', '.join(invalid_envs)))
                self.execution.has_failed_tests.value = True
                self._finalize()
                return

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
                test.reportdir = test_report.create_report_directory(self.execution.reportdir,
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
                print('WARNING: to run in debug mode, processes must equal one')

            if self.execution.processes == 1:
                # run tests serially
                for test in self.execution.tests:
                    run_test(session.testdir, self.project, test.name, test.data_set,
                             test.secrets, test.browser, test.env, session.settings,
                             test.reportdir, self.execution.has_failed_tests,
                             self.execution.tags, self.is_suite)
            else:
                # run tests using multiprocessing
                multiprocess_executor(self.project, self.execution.tests,
                                      self.execution.has_failed_tests,
                                      self.execution.processes, self.execution.tags,
                                      self.is_suite)

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
        self.report = exec_report.generate_execution_report(self.execution.reportdir,
                                                            elapsed_time,
                                                            self.execution.browsers,
                                                            self.execution.processes,
                                                            self.execution.envs,
                                                            self.execution.tags,
                                                            session.settings['remote_url'])
        if self.is_suite or len(self.execution.tests) > 1:
            self._print_results()
        # generate requested reports
        if self.is_suite:
            report_name = self.report_name or 'report'
            report_folder = self.report_folder or self.execution.reportdir
            if 'junit' in self.reports:
                junit_report.generate_junit_report(self.project, self.suite_name,
                                                   self.timestamp, self.report_folder,
                                                   report_name)
            if 'json' in self.reports and (self.report_folder or self.report_name):
                exec_report.save_execution_json_report(self.report, report_folder, report_name)
            if 'html' in self.reports:
                html_report.generate_html_report(self.project, self.suite_name,
                                                 self.timestamp, self.report_folder,
                                                 report_name)
            if 'html-no-images' in self.reports:
                if 'html' in self.reports:
                    report_name = report_name + '-no-images'
                html_report.generate_html_report(self.project, self.suite_name, self.timestamp,
                                                 self.report_folder, report_name,
                                                 no_images=True)

        # exit to the console with exit status code 1 in case a test fails
        if self.execution.has_failed_tests.value:
            sys.exit(1)
