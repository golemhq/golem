import base64
import json
import os

from golem.core import utils
from golem.report import execution_report
from golem.test_runner.conf import ResultsEnum


__test__ = False


def test_file_report_default():
    default = utils.ImmutableKeysDict(test_file=None,
                                      test=None,
                                      set_name=None,
                                      environment=None,
                                      result=None,
                                      description=None,
                                      browser=None,
                                      test_data=None,
                                      steps=[],
                                      errors=[],
                                      elapsed_time=None,
                                      timestamp=None)
    return default


def get_test_file_report_json(project, execution, timestamp, test_file, set_name=None):
    path = test_file_report_dir(test_file, project, execution, timestamp, set_name)
    path = os.path.join(path, 'report.json')
    if os.path.isfile(path):
        with open(path, 'r', encoding='utf-8') as json_file:
            return json.load(json_file)
    else:
        return None


def get_test_function_report_json(project, execution, timestamp, test_file, test_function, set_name=None):
    file_json = get_test_file_report_json(project, execution, timestamp, test_file, set_name)
    for test in file_json:
        if test['test'] == test_function:
            return test
    return None


# TODO: rename to 'get_test_report' or 'get_test_file_report'
def get_test_case_data__(project, test_file, execution, timestamp=None,
                       set_name=None, encode_screenshots=False, no_screenshots=False):
    """Retrieves all the data of a test set.

    :Args:
      - encode_screenshots: return screenshot files encoded as a base64 string or
                            the screenshot filename (rel to its folder).
      - no_screenshots: convert screenshot values to None
    """
    # TODO execution and test_set are not optional
    test_data = {
        'module': '',
        'sub_modules': '',
        'name': '',
        'test_file': '',
        'full_name': '',
        'set_name': '',
        'description': '',
        'result': '',
        'test_elapsed_time': '',
        'start_date_time': '',
        'errors': [],
        'browser': '',
        'environment': '',
        'steps': [],
        'debug_log': [],
        'info_log': [],
        'has_finished': False
    }

    report_dir = test_file_report_dir(test_file, project, execution, timestamp,
                                      test_set)
    report_json_path = os.path.join(report_dir, 'report.json')

    if os.path.isfile(report_json_path):
        test_data['has_finished'] = True
        test_full_name = '{}.{}'.format(test_file, test_function)
        with open(report_json_path, 'r', encoding='utf-8') as json_file:
            report_data = json.load(json_file)
            module = ''
            sub_modules = []
            test_split = test_file.split('.')
            if len(test_split) > 1:
                module = test_split[0]
                if len(test_split) > 2:
                    sub_modules = test_split[1:-1]
            test_data['module'] = module
            test_name = test_split[-1]
            test_data['sub_modules'] = sub_modules
            test_data['name'] = test_function
            test_data['test_file'] = test_file
            test_data['full_name'] = test_full_name
            test_data['description'] = report_data['description']
            test_data['result'] = report_data['result']
            test_data['test_elapsed_time'] = report_data['test_elapsed_time']
            start_date_time = utils.get_date_time_from_timestamp(report_data['test_timestamp'])
            test_data['start_date_time'] = start_date_time
            test_data['errors'] = report_data['errors']
            test_data['browser'] = report_data['browser']
            test_data['environment'] = report_data['environment']
            test_data['steps'] = report_data['steps']
            if no_screenshots:
                for step in test_data['steps']:
                    step['screenshot'] = None
            elif encode_screenshots:
                for step in test_data['steps']:
                    if step['screenshot'] is not None:
                        image_filename = os.path.join(report_dir, step['screenshot'])
                        b64 = base64.b64encode(open(image_filename, "rb").read()).decode('utf-8')
                        step['screenshot'] = b64
            test_data['test_set'] = test_set
            test_data['execution'] = timestamp
            test_data['data'] = report_data['test_data']
            if 'set_name' in report_data:
                test_data['set_name'] = report_data['set_name']

    debug_log_path = os.path.join(report_dir, 'execution_debug.log')
    info_log_path = os.path.join(report_dir, 'execution_info.log')
    if os.path.isfile(debug_log_path):
        with open(debug_log_path, encoding='utf-8') as log_file:
            log = log_file.readlines()
            test_data['debug_log'] = log
    if os.path.isfile(info_log_path):
        with open(info_log_path, encoding='utf-8') as log_file:
            log = log_file.readlines()
            test_data['info_log'] = log
    return test_data


def test_file_report_dir(test_name, project=None, execution=None, timestamp=None,
                         set_name='', execdir=None):
    if execdir is None:
        execdir = execution_report.execution_report_path(project, execution, timestamp)
    if set_name:
        folder_name = '{}.{}'.format(test_name, set_name)
    else:
        folder_name = test_name
    return os.path.join(execdir, folder_name)


def test_function_report_dir(project, execution, timestamp, test_file, test_function, set_name=''):
    test_file_report_path = test_file_report_dir(test_file, project, execution, timestamp, set_name)
    return os.path.join(test_file_report_path, test_function)


def _get_test_log(project, execution, timestamp, test, set_name='', level='DEBUG'):
    report_dir = test_file_report_dir(test, project, execution, timestamp, set_name)

    if level == 'DEBUG':
        logpath = os.path.join(report_dir, 'execution_debug.log')
    elif level == 'INFO':
        logpath = os.path.join(report_dir, 'execution_info.log')
    else:
        raise ValueError

    if os.path.isfile(logpath):
        with open(logpath, encoding='utf-8') as log_file:
            return log_file.read().splitlines()
    else:
        print('Log file {} not found'.format(logpath))
        return None


def get_test_debug_log(project, execution, timestamp, test, set_name=''):
    return _get_test_log(project, execution, timestamp, test, set_name=set_name, level='DEBUG')


def get_test_info_log(project, execution, timestamp, test, set_name=''):
    return _get_test_log(project, execution, timestamp, test, set_name=set_name, level='INFO')


def create_test_file_report_dir(execution_report_dir, test_name, set_name):
    """Create the directory for the report for a test file.
    If set_name is '':
      <execution_report_dir>/<test_file>/
    else:
      <execution_report_dir>/<test_file>.<set_name>/
    """
    path = test_file_report_dir(test_name, execdir=execution_report_dir, set_name=set_name)
    os.makedirs(path, exist_ok=True)
    return path


def create_test_function_report_dir(test_file_report_dir, test_function_name):
    """Create directory to store a test function report.
    The result is:
      <test_file_report_dir>/<test_function_name>/
    """
    path = os.path.join(test_file_report_dir, test_function_name)

    os.makedirs(path, exist_ok=True)
    return path


def screenshot_dir(project, execution, timestamp, test_file, test, set_name):
    return test_function_report_dir(project, execution, timestamp, test_file, test, set_name)


def screenshot_path(project, execution, timestamp, test_file, test, set_name, screenshot_file):
    path = screenshot_dir(project, execution, timestamp, test_file, test, set_name)
    return os.path.join(path, screenshot_file)


def initialize_test_file_report(test_file, tests, set_name, reportdir, environment, browser_name):
    """Given a test file and a list of test functions initialize
    test file json report with default values and result `pending`
    """
    json_report_path = os.path.join(reportdir, 'report.json')

    test_list = []

    for test in tests:
        report = test_file_report_default()
        report['test_file'] = test_file
        report['test'] = test
        report['result'] = ResultsEnum.PENDING
        report['set_name'] = set_name
        report['environment'] = environment
        report['browser'] = browser_name
        test_list.append(report)

    with open(json_report_path, 'w', encoding='utf-8') as f:
        json.dump(test_list, f, indent=4, ensure_ascii=False)


def generate_report(test_file_name, result, test_data, reportdir):
    """Adds the report of a test function to a test_file report.json"""
    json_report_path = os.path.join(reportdir, 'report.json')
    # short_error = ''
    # if result['error']:
    #     short_error = '\n'.join(result['error'].split('\n')[-2:])

    # TODO
    serialized_data = {}
    for key, value in test_data.items():
        try:
            json.dumps('{"{}":"{}"}'.format(key, value))
            serialized_data[key] = value
        except:
            serialized_data[key] = repr(value)

    env_name = ''
    if 'env' in test_data:
        if 'name' in test_data.env:
            env_name = test_data.env.name

    browser = result['browser']
    output_browser = result['browser']
    if result['browser_capabilities'] and 'browserName' in result['browser_capabilities']:
        output_browser = '{} - {}'.format(result['browser'], result['browser_capabilities']['browserName'])
    elif browser == 'chrome-remote':
        output_browser = 'chrome (remote)'
    elif browser == 'chrome-headless':
        output_browser = 'chrome (headless)'
    elif browser == 'chrome-remote-headless':
        output_browser = 'chrome (remote, headless)'
    elif browser == 'firefox-remote':
        output_browser = 'firefox (remote)'

    report = test_file_report_default()
    report['test_file'] = test_file_name
    report['test'] = result['name']
    report['set_name'] = result['set_name']
    report['environment'] = env_name
    report['result'] = result['result']
    report['description'] = result['description']
    report['browser'] = output_browser
    report['test_data'] = serialized_data
    report['steps'] = result['steps']
    report['errors'] = result['errors']
    report['elapsed_time'] = result['test_elapsed_time']
    report['timestamp'] = result['test_timestamp']

    if os.path.isfile(json_report_path):
        with open(json_report_path, 'r', encoding='utf-8') as json_file:
            report_data = json.load(json_file)
    else:
        report_data = []

    index = None
    for i, test in enumerate(report_data):
        if test['test'] == result['name']:
            index = i
    if index is None:
        report_data.append(report)
    else:
        report_data[index] = report

    with open(json_report_path, 'w', encoding='utf-8') as json_file:
        json.dump(report_data, json_file, indent=4, ensure_ascii=False)
