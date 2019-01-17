"""Helper functions to deal with Golem GUI module application."""
import os
import sys
import errno
import subprocess
import inspect
from functools import wraps

from flask import abort, render_template
from flask_login import current_user

import golem.actions
from golem.core import utils, test_execution
from golem.gui import report_parser


def run_test_case(project, test_case_name, browsers=None, environments=None, processes=1):
    """Run a test case. This is used when running tests from the GUI"""
    script_name = sys.argv[0]
    timestamp = utils.get_timestamp()
    param_list = [script_name, 'run', project, test_case_name, '--timestamp', timestamp]

    if browsers:
        param_list.append('--browsers')
        for browser in browsers:
            param_list.append(browser)
    if environments:
        param_list.append('--environments')
        for environment in environments:
            param_list.append(environment)
    if processes:
        param_list.append('--threads')
        param_list.append(str(processes))

    subprocess.Popen(param_list)
    return timestamp


def run_suite(project, suite_name):
    """Run a suite. This is used when running suites from the GUI"""
    script_name = sys.argv[0]
    timestamp = utils.get_timestamp()
    subprocess.Popen([script_name, 'run', project, suite_name, '--timestamp', timestamp])
    return timestamp


class Golem_action_parser:
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

    def __new__(cls):
        if Golem_action_parser.__instance is None:
            Golem_action_parser.__instance = object.__new__(cls)
        return Golem_action_parser.__instance

    def _is_module_function(self, mod, func):
        return inspect.isfunction(func) and inspect.getmodule(func) == mod

    def _parse_docstring(self, docstring):
        docstring_def = {
            'description': '',
            'parameters': []
        }
        split = docstring.split('Parameters:')
        desc_lines = [x.strip() for x in split[0].splitlines() if len(x.strip())]
        description = ' '.join(desc_lines)
        docstring_def['description'] = description
        if len(split) == 2:
            param_lines = [x.strip() for x in split[1].splitlines() if len(x.strip())]
            for param_line in param_lines:
                param_parts = param_line.split(':')
                param = {
                    'name': param_parts[0].strip(),
                    'type': param_parts[1].strip()
                }
                docstring_def['parameters'].append(param)
        return docstring_def

    def get_actions(self):
        if not self.actions:
            actions = []
            module = golem.actions

            def is_valid_function(function, module):
                if self._is_module_function(module, function):
                    if not function.__name__.startswith('_'):
                        return True
                return False

            action_func_list = [function for function in module.__dict__.values()
                                if is_valid_function(function, module)]
            for action in action_func_list:
                doc = action.__doc__
                if doc is None:
                    print('Warning: action {} does not have docstring defined'
                          .format(action.__name__))
                elif 'DEPRECATED' in doc:
                    pass
                else:
                    action_def = self._parse_docstring(doc)
                    action_def['name'] = action.__name__
                    actions.append(action_def)
            self.actions = actions
        return self.actions


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
        if not utils.project_exists(test_execution.root_path, kwargs['project']):
            abort(404, 'The project {} does not exist.'.format(kwargs['project']))
        return func(*args, **kwargs)
    return wrapper


def gui_permissions_required(func):
    """A wrapper that checks if the current user
    has GUI permissions to the project.
      * The annotated function must have a `project` argument.
      * The current user must be available in `flask_login.current_user`
      * The user object must have a `has_gui_permissions(project) method`
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.has_gui_permissions(kwargs['project']):
            return render_template('not_permission.html')
        return func(*args, **kwargs)
    return wrapper


def report_permissions_required(func):
    """A wrapper that checks if the current user
    has project permissions to the project.
      * The annotated function must have a `project` argument.
      * The current user must be available in `flask_login.current_user`
      * The user object must have a `has_report_permissions(project) method`
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.has_report_permissions(kwargs['project']):
            return render_template('not_permission.html')
        return func(*args, **kwargs)
    return wrapper


def generate_html_report(project, suite, execution, report_directory=None,
                         report_name=None, no_images=False):
    """Generate static HTML report.
    Report is generated in <report_directory>/<report_name>
    By default it's generated in <testdir>/projects/<project>/reports/<suite>/<timestamp>
    Default name is 'report.html' and 'report-no-images.html'
    """
    from golem import gui
    app = gui.app
    if not report_directory:
        report_directory = os.path.join(test_execution.root_path, 'projects', project,
                                        'reports', suite, execution)
    if not report_name:
        if no_images:
            report_name = 'report-no-images'
        else:
            report_name = 'report'

    formatted_date = report_parser.get_date_time_from_timestamp(execution)
    css = {}
    js = {}
    boostrap_path = os.path.join(app.static_folder, 'css', 'bootstrap', 'bootstrap.min.css')
    datatables_js = os.path.join(app.static_folder, 'js', 'external', 'datatable', 'datatables.min.js')
    css['bootstrap'] = open(boostrap_path).read()
    css['main'] = open(os.path.join(app.static_folder, 'css', 'main.css')).read()
    css['report'] = open(os.path.join(app.static_folder, 'css', 'report.css')).read()
    js['jquery'] = open(os.path.join(app.static_folder, 'js', 'external', 'jquery.min.js')).read()
    js['datatables'] = open(datatables_js).read()
    js['bootstrap'] = open(os.path.join(app.static_folder, 'js', 'external', 'bootstrap.min.js')).read()
    js['main'] = open(os.path.join(app.static_folder, 'js', 'main.js')).read()
    js['report_execution'] = open(os.path.join(app.static_folder, 'js', 'report_execution.js')).read()
    execution_data = report_parser.get_execution_data(workspace=test_execution.root_path,
                                                      project=project, suite=suite,
                                                      execution=execution)
    detail_test_data = {}
    for test in execution_data['tests']:
        test_detail = report_parser.get_test_case_data(test_execution.root_path, project,
                                                       test['full_name'], suite=suite,
                                                       execution=execution,
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
    report_directory = os.path.join(test_execution.root_path, 'projects', project,
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
