import base64
import json
import os
import uuid

from golem.core import session, utils


def get_test_case_data(project, test, suite=None, execution=None, test_set=None,
                       is_single=False, encode_screenshots=False, no_screenshots=False):
    """Retrieves all the data of a single test execution.

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
        'full_name': '',
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
    if is_single:
        test_dir = os.path.join(session.testdir, 'projects', project, 'reports',
                                'single_tests', test, execution, test_set)
    else:
        test_dir = os.path.join(session.testdir, 'projects', project, 'reports',
                                suite, execution, test, test_set)
    report_json_path = os.path.join(test_dir, 'report.json')
    if os.path.isfile(report_json_path):
        test_data['has_finished'] = True
        with open(report_json_path, 'r') as json_file:
            report_data = json.load(json_file)
            module = ''
            sub_modules = []
            test_split = test.split('.')
            if len(test_split) > 1:
                module = test_split[0]
                if len(test_split) > 2:
                    sub_modules = test_split[1:-1]
            test_data['module'] = module
            test_name = test_split[-1]
            test_data['sub_modules'] = sub_modules
            test_data['name'] = test_name
            test_data['full_name'] = test
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
                        image_filename = os.path.join(test_dir, step['screenshot'])
                        b64 = base64.b64encode(open(image_filename, "rb").read()).decode('utf-8')
                        step['screenshot'] = b64
            test_data['test_set'] = test_set
            test_data['execution'] = execution
            test_data['data'] = report_data['test_data']
            if 'set_name' in report_data:
                test_data['set_name'] = report_data['set_name']

    debug_log_path = os.path.join(test_dir, 'execution_debug.log')
    info_log_path = os.path.join(test_dir, 'execution_info.log')
    if os.path.isfile(debug_log_path):
        with open(debug_log_path) as log_file:
            log = log_file.readlines()
            test_data['debug_log'] = log
    if os.path.isfile(info_log_path):
        with open(info_log_path) as log_file:
            log = log_file.readlines()
            test_data['info_log'] = log
    return test_data


def create_report_directory(execution_directory, test_case_name, is_suite):
    """Create directory to store a single test report.

    execution_directory takes the following format for suites:
      <testdir>/projects/<project>/reports/<suite_name>/<timestamp>/
    and this format for single tests
      <testdir>/projects/<project>/reports/<suite_name>/<timestamp>/

    The result for suites is:
      <execution_directory>/<test_name>/<set_name>/
    and for single tests is:
      <execution_directory>/<set_name>/
    """
    set_name = 'set_' + str(uuid.uuid4())[:6]
    # create suite execution folder in reports directory
    if is_suite:
        report_directory = os.path.join(execution_directory, test_case_name, set_name)
    else:
        report_directory = os.path.join(execution_directory, set_name)
    if not os.path.isdir(report_directory):
        try:
            os.makedirs(report_directory)
        except:
            pass
    return report_directory


def generate_report(report_directory, test_case_name, test_data, result):
    """Generate the json report for a single test execution."""
    json_report_path = os.path.join(report_directory, 'report.json')
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
    if result['browser_full_name']:
        output_browser = '{} - {}'.format(result['browser'], result['browser_full_name'])
    elif browser == 'chrome-remote':
        output_browser = 'chrome (remote)'
    elif browser == 'chrome-headless':
        output_browser = 'chrome (headless)'
    elif browser == 'chrome-remote-headless':
        output_browser = 'chrome (remote, headless)'
    elif browser == 'firefox-remote':
        output_browser = 'firefox (remote)'

    report = {
        'test_case': test_case_name,
        'result': result['result'],
        'steps': result['steps'],
        'errors': result['errors'],
        'description': result['description'],
        'browser': output_browser,
        'test_data': serialized_data,
        'environment': env_name,
        'set_name': result['set_name'],
        'test_elapsed_time': result['test_elapsed_time'],
        'test_timestamp': result['test_timestamp']
    }
    with open(json_report_path, 'w', encoding='utf-8') as json_file:
        json.dump(report, json_file, indent=4)
