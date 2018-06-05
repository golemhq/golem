"""Helper functions to deal with Golem GUI module application."""
import datetime
import os
import subprocess
import inspect

import golem.actions
from golem.core import utils


def run_test_case(project, test_case_name, environment):
    """Run a test case. This is used when running tests from the GUI"""
    timestamp = utils.get_timestamp()
    param_list = ['golem','run', project, test_case_name,
                  '--timestamp', timestamp]
    if environment:
        param_list.append('--environments')
        param_list.append(environment)
    subprocess.Popen(param_list)
    return timestamp


def run_suite(project, suite_name):
    """Run a suite. This is used when running suites from the GUI"""
    timestamp = utils.get_timestamp()
    subprocess.Popen(['golem', 'run', project, suite_name,
                      '--timestamp', timestamp])
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
        param1  element
        param2  value
        param3 (int, float)  value
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
        'firefox-remote',
        'ie',
        'ie-remote',
        'opera',
        'opera-remote',
        # 'safari',
        # 'safari-remote'
    ]
    return supported_browsers

