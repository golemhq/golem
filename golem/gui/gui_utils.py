import datetime
import os
import subprocess

from golem.core import utils


def new_directory(root_path, project, parents, dir_name, dir_type):
    """Creates a new directory for suites, tests or pages.
    if the directory is inside other directories, these should already exist.
    parents is a list of parent directories.
    dir_type should be in: ['tests', 'suites', 'pages']"""
    parents = os.sep.join(parents)
    path = os.path.join(root_path, 'projects', project, dir_type, parents, dir_name)
    errors = []
    if os.path.exists(path):
        errors.append('A directory with that name already exists')
    else:
        utils.create_new_directory(path=path, add_init=True)
    return errors


# def new_directory_page_object(root_path, project, parents, dir_name):
#     parents = os.sep.join(parents)
#     errors = []
#     if directory_already_exists(root_path, project, 'pages', parents, dir_name):
#         errors.append('A directory with that name already exists')
#     else:
#         path_list = [root_path, 'projects', project, 'pages', parents, dir_name]
#         utils.create_new_directory(path_list=path_list, add_init=True)
#     return errors


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


def get_global_actions():
    global_actions = [
        {
            'name': 'assert contains',
            'parameters': [{'name': 'element', 'type': 'value'},
                           {'name': 'value', 'type': 'value'}]
        },
        {
            'name': 'assert equals',
            'parameters': [{'name': 'actual value', 'type': 'value'},
                           {'name': 'expected value', 'type': 'value'}]
        },
        {
            'name': 'assert false',
            'parameters': [{'name': 'condition', 'type': 'value'}]
        },
        {
            'name': 'assert true',
            'parameters': [{'name': 'condition', 'type': 'value'}]
        },
        {
            'name': 'capture',
            'parameters': [{'name': 'message (optional)', 'type': 'value'}]
        },
        {
            'name': 'clear',
            'parameters': [{'name': 'element', 'type': 'element'}]
        },
        {
            'name': 'click',
            'parameters': [{'name': 'element', 'type': 'element'}]
        },
        {
            'name': 'close',
            'parameters': []
        },
        {
            'name': 'debug',
            'parameters': []
        },
        {
            'name': 'get',
            'parameters': [{'name': 'url', 'type': 'value'}]
        },
        {
            'name': 'http_get',
            'parameters': [{'name': 'url', 'type': 'value'},
                           {'name': 'headers', 'type': 'multiline-value'},
                           {'name': 'params', 'type': 'value'},
                           {'name': 'verify SSL certificate', 'type': 'value'}]
        },
        {
            'name': 'http_post',
            'parameters': [{'name': 'url', 'type': 'value'},
                           {'name': 'headers', 'type': 'value'},
                           {'name': 'data', 'type': 'value'},
                           {'name': 'verify SSL certificate', 'type': 'value'}]
        },
        {
            'name': 'navigate',
            'parameters': [{'name': 'url', 'type': 'value'}]
        },
        {
            'name': 'press key',
            'parameters': [{'name': 'element', 'type': 'element'},
                           {'name': 'key', 'type': 'value'}]
        },
        {
            'name': 'random',
            'parameters': [{'name': 'args', 'type': 'value'}]
        },
        {
            'name': 'refresh page',
            'parameters': []
        },
        {
            'name': 'select by index',
            'parameters': [{'name': 'from element', 'type': 'element'},
                           {'name': 'index', 'type': 'value'}]
        },
        {
            'name': 'select by text',
            'parameters': [{'name': 'from element', 'type': 'element'},
                           {'name': 'text', 'type': 'value'}]
        },
        {
            'name': 'select by value',
            'parameters': [{'name': 'from element', 'type': 'element'},
                           {'name': 'value', 'type': 'value'}]
        },
        {
            'name': 'send keys',
            'parameters': [{'name': 'element', 'type': 'element'},
                           {'name': 'value', 'type': 'value'}]
        },
        {
            'name': 'set window size',
            'parameters': [{'name': 'width', 'type': 'value'},
                           {'name': 'height', 'type': 'value'}]
        },
        {
            'name': 'step',
            'parameters': [{'name': 'message', 'type': 'value'}]
        },
        {
            'name': 'store',
            'parameters': [{'name': 'key', 'type': 'value'},
                           {'name': 'value', 'type': 'value'}]
        },
        {
            'name': 'verify exists',
            'parameters': [{'name': 'element', 'type': 'element'}]
        },
        {
            'name': 'verify is enabled',
            'parameters': [{'name': 'element', 'type': 'element'}]
        },
        {
            'name': 'verify is not enabled',
            'parameters': [{'name': 'element', 'type': 'element'}]
        },
        {
            'name': 'verify is not selected',
            'parameters': [{'name': 'element', 'type': 'element'}]
        },
        {
            'name': 'verify is not visible',
            'parameters': [{'name': 'element', 'type': 'element'}]
        },
        {
            'name': 'verify is selected',
            'parameters': [{'name': 'element', 'type': 'element'}]
        },
        {
            'name': 'verify is visible',
            'parameters': [{'name': 'element', 'type': 'element'}]
        },
        {
            'name': 'verify not exists',
            'parameters': [{'name': 'element', 'type': 'element'}]
        },
        {
            'name': 'verify selected option',
            'parameters': [{'name': 'select', 'type': 'element'},
                           {'name': 'text option', 'type': 'value'}]
        },
        {
            'name': 'verify text',
            'parameters': [{'name': 'text', 'type': 'value'}]
        },
        {
            'name': 'verify text in element',
            'parameters': [{'name': 'element', 'type': 'element'},
                           {'name': 'text', 'type': 'value'}]
        },
        {
            'name': 'wait',
            'parameters': [{'name': 'seconds', 'type': 'value'}]
        },
        {
            'name': 'wait for element visible',
            'parameters': [{'name': 'element', 'type': 'element'},
                           {'name': 'timeout (optional)', 'type': 'value'}]
        },
        {
            'name': 'wait for element not visible',
            'parameters': [{'name': 'element', 'type': 'element'},
                           {'name': 'timeout (optional)', 'type': 'value'}]
        },
        {
            'name': 'wait for element enabled',
            'parameters': [{'name': 'element', 'type': 'element'},
                           {'name': 'timeout (optional)', 'type': 'value'}]
        }
    ]
    return global_actions


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
