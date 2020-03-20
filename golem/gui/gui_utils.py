"""Helper functions to deal with Golem GUI module application."""
import configparser
import copy
import errno
import inspect
import os
import subprocess
import sys
from functools import wraps
from urllib.parse import urlparse, urljoin

from flask import abort, render_template, request
from flask_login import current_user

import golem.actions
from golem.core import utils, session, errors, test_directory, settings_manager
from golem.gui import report_parser
from golem.gui.user_management import Permissions
from golem import gui


DEFAULT_SECRET_KEY = 'd3dac3po6c994b5590bf7fr2d2db355c661cbb83dec6344408'


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def run_test(project, test_name, browsers=None, environments=None, processes=1):
    """Run a test case. This is used when running tests from the GUI"""
    script_name = sys.argv[0]
    timestamp = utils.get_timestamp()
    param_list = [
        script_name,
        '--golem-dir',
        session.testdir,
        'run',
        project,
        test_name,
        '--timestamp',
        timestamp]

    if browsers:
        param_list.append('--browsers')
        for browser in browsers:
            param_list.append(browser)
    if environments:
        param_list.append('--environments')
        for environment in environments:
            param_list.append(environment)
    if processes:
        param_list.append('--processes')
        param_list.append(str(processes))

    subprocess.Popen(param_list)
    return timestamp


def run_suite(project, suite_name):
    """Run a suite. This is used when running suites from the GUI"""
    script_name = sys.argv[0]
    timestamp = utils.get_timestamp()
    subprocess.Popen([script_name, 'run', project, suite_name, '--timestamp', timestamp])
    return timestamp


class GolemActionParser:
    """Generates a list of golem actions by reading the functions docstrings

    This class is a singleton. The list of action definitions
    is cached so only the first time they are required will be
    retrieved by parsing the golem.actions module

    This class expects the docstrings of the actions to have this format:
    def some_action(param1, param2, param3):
        '''This is the description of the action function
        
        parameters:
        param1 : element
        param2 : value
        param3 (int, float) :  value
        '''

    This would generate the following list:
    actions = [
        {
            'name': 'some_action',
            'description': 'This is the description of the action'
            'parameters': [{'name': 'param1', 'type': 'element'},
                           {'name': 'param2', 'type': 'value'},
                           {'name': 'param3 (int, float)', 'type': 'value'}]
        }
    ]

    Note: the `type` distinction (element or value) is used by the GUI
    test builder because it needs to know if it should use element
    autocomplete (page object elements) or data autocomplete
    (columns of the datatable)
    """
    __instance = None
    actions = None
    explicit_actions = None

    def __new__(cls):
        if GolemActionParser.__instance is None:
            GolemActionParser.__instance = object.__new__(cls)
        return GolemActionParser.__instance

    @staticmethod
    def _is_module_function(mod, func):
        return inspect.isfunction(func) and inspect.getmodule(func) == mod

    @staticmethod
    def _parse_docstring(docstring):
        description = ''
        parameters = []
        split = docstring.split('Parameters:')
        desc_lines = [x.strip() for x in split[0].splitlines() if len(x.strip())]
        description = ' '.join(desc_lines)
        if len(split) == 2:
            param_lines = [x.strip() for x in split[1].splitlines() if len(x.strip())]
            for param_line in param_lines:
                param_parts = param_line.split(':')
                param = {
                    'name': param_parts[0].strip(),
                    'type': param_parts[1].strip()
                }
                parameters.append(param)
        return description, parameters

    def _get_actions(self):
        actions = []
        actions_module = golem.actions

        def is_valid_function(function, module):
            """A valid action function must be defined
            in the actions module and must not start
            with underscore
            """
            if self._is_module_function(module, function):
                if not function.__name__.startswith('_'):
                    return True
            return False

        action_func_list = [function for function in actions_module.__dict__.values()
                            if is_valid_function(function, actions_module)]
        for action in action_func_list:
            doc = action.__doc__
            if doc is None:
                print('Warning: action {} does not have docstring defined'
                      .format(action.__name__))
            elif 'DEPRECATED' in doc:
                pass
            else:
                description, parameters = self._parse_docstring(doc)
                action_def = {
                    'name': action.__name__,
                    'description': description,
                    'parameters': parameters
                }
                actions.append(action_def)

        explicit_actions = copy.deepcopy(actions)
        for action in explicit_actions:
            action['name'] = 'actions.{}'.format(action['name'])

        # add 'code_block' action
        code_block_action = {
            'description': 'Insert code block',
            'parameters': [],
            'name': 'code_block'
        }
        actions.append(code_block_action)
        explicit_actions.append(code_block_action)

        self.actions = actions
        self.explicit_actions = explicit_actions

    def get_actions(self, project_name=None):
        if self.actions is None:
            self._get_actions()

        if project_name:
            settings = settings_manager.get_project_settings(project_name)
        else:
            settings = settings_manager.get_global_settings()

        if settings['implicit_actions_import']:
            return self.actions
        else:
            return self.explicit_actions


def get_supported_browsers_suggestions():
    """Return a list of supported browsers by default."""
    supported_browsers = [
        'chrome',
        'chrome-remote',
        'chrome-headless',
        'chrome-remote-headless',
        'edge',
        'edge-remote',
        'firefox',
        'firefox-headless',
        'firefox-remote',
        'firefox-remote-headless',
        'ie',
        'ie-remote',
        'opera',
        'opera-remote',
    ]
    return supported_browsers


def project_exists(func):
    """A wrapper that checks if the requested project exists.
      * The annotated function must have a `project` argument.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not test_directory.project_exists(kwargs['project']):
            abort(404, 'The project {} does not exist.'.format(kwargs['project']))
        return func(*args, **kwargs)
    return wrapper


def permission_required(permission):
    """A wrapper that checks if the current user
    has the required permissions for a page
      * The annotated function must have a `project` argument for project pages.
      * The current user must be available in `flask_login.current_user`
      * The user object must have a `project_weight(project) method`
    """
    def check_permissions(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_superuser:
                project = kwargs.get('project', None)
                if project:
                    user_weight = current_user.project_weight(project)
                else:
                    user_weight = 0
                required_weight = Permissions.get_weight(permission)
                if user_weight < required_weight:
                    return render_template('not_permission.html')
            return func(*args, **kwargs)
        return wrapper
    return check_permissions


def generate_html_report(project, suite, execution, report_directory=None,
                         report_name=None, no_images=False):
    """Generate static HTML report.
    Report is generated in <report_directory>/<report_name>
    By default it's generated in <testdir>/projects/<project>/reports/<suite>/<timestamp>
    Default name is 'report.html' and 'report-no-images.html'
    """
    if not report_directory:
        report_directory = os.path.join(session.testdir, 'projects', project,
                                        'reports', suite, execution)
    if not report_name:
        if no_images:
            report_name = 'report-no-images'
        else:
            report_name = 'report'

    formatted_date = report_parser.get_date_time_from_timestamp(execution)
    app = gui.create_app()
    static_folder = app.static_folder
    css = {}
    js = {}
    boostrap_path = os.path.join(static_folder, 'css', 'bootstrap', 'bootstrap.min.css')
    datatables_js = os.path.join(static_folder, 'js', 'external', 'datatable', 'datatables.min.js')
    css['bootstrap'] = open(boostrap_path).read()
    css['main'] = open(os.path.join(static_folder, 'css', 'main.css')).read()
    css['report'] = open(os.path.join(static_folder, 'css', 'report.css')).read()
    js['jquery'] = open(os.path.join(static_folder, 'js', 'external', 'jquery.min.js')).read()
    js['datatables'] = open(datatables_js).read()
    js['bootstrap'] = open(os.path.join(static_folder, 'js', 'external', 'bootstrap.min.js')).read()
    js['main'] = open(os.path.join(static_folder, 'js', 'main.js')).read()
    js['report_execution'] = open(os.path.join(static_folder, 'js', 'report_execution.js')).read()
    execution_data = report_parser.get_execution_data(project=project, suite=suite, execution=execution)
    detail_test_data = {}
    for test in execution_data['tests']:
        test_detail = report_parser.get_test_case_data(project, test['full_name'],
                                                       suite=suite, execution=execution,
                                                       test_set=test['test_set'],
                                                       is_single=False,
                                                       encode_screenshots=True,
                                                       no_screenshots=no_images)
        detail_test_data[test['test_set']] = test_detail
    with app.app_context():
        html_string = render_template('report/report_execution_static.html', project=project,
                                      suite=suite, execution=execution, execution_data=execution_data,
                                      detail_test_data=detail_test_data, formatted_date=formatted_date,
                                      css=css, js=js, static=True)
    _, file_extension = os.path.splitext(report_name)
    if not file_extension:
        report_name = '{}.html'.format(report_name)
    destination = os.path.join(report_directory, report_name)

    if not os.path.exists(os.path.dirname(destination)):
        os.makedirs(os.path.dirname(destination), exist_ok=True)

    try:
        with open(destination, 'w') as f:
            f.write(html_string)
    except IOError as e:
        if e.errno == errno.EACCES:
            print('ERROR: cannot write to {}, PermissionError (Errno 13)'
                  .format(destination))
        else:
            print('ERROR: There was an error writing to {}'.format(destination))

    return html_string


def get_or_generate_html_report(project, suite, execution, no_images=False):
    """Get the HTML report as a string.
    If it does not exist, generate it:
    Report is generated at
    <testdir>/projects/<project>/reports/<suite>/<execution>/report.html|report-no-images.html
    """
    if no_images:
        report_filename = 'report-no-images'
    else:
        report_filename = 'report'
    report_directory = os.path.join(session.testdir, 'projects', project,
                                    'reports', suite, execution)
    report_filepath = os.path.join(report_directory, report_filename + '.html')
    if os.path.isfile(report_filepath):
        html_string = open(report_filepath).read()
    else:
        html_string = generate_html_report(project, suite, execution,
                                           report_directory=report_directory,
                                           report_name=report_filename,
                                           no_images=no_images)
    return html_string


def get_secret_key():
    """Try to get the secret key from the .golem file
    located in the test directory.
    A default secret key will be returned if the .golem file
    does not have a secret key defined.

    Example .golem file:
    [gui]
    secret_key = my_secret_key_string
    """
    golem_file = os.path.join(session.testdir, '.golem')
    if not os.path.isfile(golem_file):
        sys.exit(errors.invalid_test_directory.format(session.testdir))
    config = configparser.ConfigParser()
    config.read(golem_file)
    if 'gui' not in config:
        print('Warning: gui config section not found in .golem file. Using default secret key')
        secret_key = DEFAULT_SECRET_KEY
    elif 'secret_key' not in config['gui']:
        print('Warning: secret_key not found in .golem file. Using default secret key')
        secret_key = DEFAULT_SECRET_KEY
    else:
        secret_key = config['gui']['secret_key']
    return secret_key


class ProjectsCache:
    """A cache of projects.
    The cache should be updated when projects are added or removed.
    """

    _projects = None

    @staticmethod
    def get():
        if ProjectsCache._projects is None:
            ProjectsCache._projects = test_directory.get_projects()
        return ProjectsCache._projects

    @staticmethod
    def get_user_projects():
        return [p for p in ProjectsCache.get() if p in current_user.project_list ]

    @staticmethod
    def add(project_name):
        ProjectsCache.get()
        ProjectsCache._projects.append(project_name)

    @staticmethod
    def remove(project_name):
        ProjectsCache.get()
        if project_name in ProjectsCache._projects:
            ProjectsCache._projects.remove(project_name)
