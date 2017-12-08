import datetime
import os
import subprocess
import inspect

import golem.actions
from golem.core import utils


def run_test_case(project, test_case_name, environment):
    timestamp = utils.get_timestamp()
    param_list = ['python', 'golem.py','run',
                  project,
                  test_case_name,
                  '--timestamp', timestamp]
    if environment:
        param_list.append('--environments')
        param_list.append(environment)
    subprocess.Popen(param_list)
    return timestamp


def run_suite(project, suite_name):
    timestamp = utils.get_timestamp()
    subprocess.Popen(['python', 'golem.py', 'run', project, suite_name, '--timestamp', timestamp])
    return timestamp


def directory_already_exists(root_path, project, root_dir, parents, dir_name):
    parents_joined = os.sep.join(parents)
    directory_path = os.path.join(root_path, 'projects', project, root_dir,
                                  parents_joined, dir_name)
    return bool(os.path.exists(directory_path))


def time_to_string():
    time_format = '%Y-%m-%d-%H-%M-%S-%f'
    return datetime.datetime.now().strftime(time_format)


def string_to_time(time_string):
    return datetime.datetime.strptime(time_string, '%Y-%m-%d-%H-%M-%S-%f')


class Golem_action_parser:
    """Generates a list of golem actions by reading the functions docstrings

    This class is a singleton.

    The list of action definitions is cached so only the first time
    they are required will be retrieved by parsing the golem.actions module

    This class expects the docstrings of the actions to have this format:

    def some_action(param1, param2, param3):
        '''This is the description of the action
        
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

    Note: the `type` distinction (element or value) is used by the GUI test builder
    because it needs to know if it should use element autocomplete (page
    object elements) or data autocomplete (columns of the datatable)
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
                else:
                    action_def = self._parse_docstring(doc)
                    action_def['name'] = action.__name__
                    actions.append(action_def)
            self.actions = actions

        return self.actions

# TODO deprecated
# def get_global_actions():

#     global_actions = [
#         {
#             'name': 'assert contains',
#             'parameters': [{'name': 'element', 'type': 'value'},
#                            {'name': 'value', 'type': 'value'}]
#         },
#         {
#             'name': 'assert equals',
#             'parameters': [{'name': 'actual value', 'type': 'value'},
#                            {'name': 'expected value', 'type': 'value'}]
#         },
#         {
#             'name': 'assert false',
#             'parameters': [{'name': 'condition', 'type': 'value'}]
#         },
#         {
#             'name': 'assert true',
#             'parameters': [{'name': 'condition', 'type': 'value'}]
#         },
#         {
#             'name': 'capture',
#             'parameters': [{'name': 'message (optional)', 'type': 'value'}]
#         },
#         {
#             'name': 'clear',
#             'parameters': [{'name': 'element', 'type': 'element'}]
#         },
#         {
#             'name': 'click',
#             'parameters': [{'name': 'element', 'type': 'element'}]
#         },
#         {
#             'name': 'close',
#             'parameters': []
#         },
#         {
#             'name': 'debug',
#             'parameters': []
#         },
#         {
#             'name': 'get',
#             'parameters': [{'name': 'url', 'type': 'value'}]
#         },
#         {
#             'name': 'http_get',
#             'parameters': [{'name': 'url', 'type': 'value'},
#                            {'name': 'headers', 'type': 'multiline-value'},
#                            {'name': 'params', 'type': 'value'},
#                            {'name': 'verify SSL certificate', 'type': 'value'}]
#         },
#         {
#             'name': 'http_post',
#             'parameters': [{'name': 'url', 'type': 'value'},
#                            {'name': 'headers', 'type': 'value'},
#                            {'name': 'data', 'type': 'value'},
#                            {'name': 'verify SSL certificate', 'type': 'value'}]
#         },
#         {
#             'name': 'navigate',
#             'parameters': [{'name': 'url', 'type': 'value'}]
#         },
#         {
#             'name': 'press key',
#             'parameters': [{'name': 'element', 'type': 'element'},
#                            {'name': 'key', 'type': 'value'}]
#         },
#         {
#             'name': 'random',
#             'parameters': [{'name': 'args', 'type': 'value'}]
#         },
#         {
#             'name': 'refresh page',
#             'parameters': []
#         },
#         {
#             'name': 'select by index',
#             'parameters': [{'name': 'from element', 'type': 'element'},
#                            {'name': 'index', 'type': 'value'}]
#         },
#         {
#             'name': 'select by text',
#             'parameters': [{'name': 'from element', 'type': 'element'},
#                            {'name': 'text', 'type': 'value'}]
#         },
#         {
#             'name': 'select by value',
#             'parameters': [{'name': 'from element', 'type': 'element'},
#                            {'name': 'value', 'type': 'value'}]
#         },
#         {
#             'name': 'send keys',
#             'parameters': [{'name': 'element', 'type': 'element'},
#                            {'name': 'value', 'type': 'value'}]
#         },
#         {
#             'name': 'set window size',
#             'parameters': [{'name': 'width', 'type': 'value'},
#                            {'name': 'height', 'type': 'value'}]
#         },
#         {
#             'name': 'step',
#             'parameters': [{'name': 'message', 'type': 'value'}]
#         },
#         {
#             'name': 'store',
#             'parameters': [{'name': 'key', 'type': 'value'},
#                            {'name': 'value', 'type': 'value'}]
#         },
#         {
#             'name': 'verify exists',
#             'parameters': [{'name': 'element', 'type': 'element'}]
#         },
#         {
#             'name': 'verify is enabled',
#             'parameters': [{'name': 'element', 'type': 'element'}]
#         },
#         {
#             'name': 'verify is not enabled',
#             'parameters': [{'name': 'element', 'type': 'element'}]
#         },
#         {
#             'name': 'verify is not selected',
#             'parameters': [{'name': 'element', 'type': 'element'}]
#         },
#         {
#             'name': 'verify is not visible',
#             'parameters': [{'name': 'element', 'type': 'element'}]
#         },
#         {
#             'name': 'verify is selected',
#             'parameters': [{'name': 'element', 'type': 'element'}]
#         },
#         {
#             'name': 'verify is visible',
#             'parameters': [{'name': 'element', 'type': 'element'}]
#         },
#         {
#             'name': 'verify not exists',
#             'parameters': [{'name': 'element', 'type': 'element'}]
#         },
#         {
#             'name': 'verify selected option',
#             'parameters': [{'name': 'select', 'type': 'element'},
#                            {'name': 'text option', 'type': 'value'}]
#         },
#         {
#             'name': 'verify text',
#             'parameters': [{'name': 'text', 'type': 'value'}]
#         },
#         {
#             'name': 'verify text in element',
#             'parameters': [{'name': 'element', 'type': 'element'},
#                            {'name': 'text', 'type': 'value'}]
#         },
#         {
#             'name': 'wait',
#             'parameters': [{'name': 'seconds', 'type': 'value'}]
#         },
#         {
#             'name': 'wait for element visible',
#             'parameters': [{'name': 'element', 'type': 'element'},
#                            {'name': 'timeout (optional)', 'type': 'value'}]
#         },
#         {
#             'name': 'wait for element not visible',
#             'parameters': [{'name': 'element', 'type': 'element'},
#                            {'name': 'timeout (optional)', 'type': 'value'}]
#         },
#         {
#             'name': 'wait for element enabled',
#             'parameters': [{'name': 'element', 'type': 'element'},
#                            {'name': 'timeout (optional)', 'type': 'value'}]
#         }
#     ]
#     return global_actions


def get_supported_browsers_suggestions():
    supported_browsers = [
        'chrome',
        'chrome-remote',
        'chrome-headless',
        'chrome-remote-headless',
        'firefox',
        'firefox-remote',
        'ie',
        'ie-remote'
    ]
    return supported_browsers

