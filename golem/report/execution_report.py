import base64
import errno
import json
import os

from golem.core import utils
from golem.core.project import Project
from golem.report import test_report
from golem.test_runner.conf import ResultsEnum


def execution_report_default():
    params = utils.ImmutableKeysDict(browsers=[],
                                     processes=None,
                                     environments=[],
                                     tags=[],
                                     remote_url='')

    execution_report = utils.ImmutableKeysDict(tests=[],
                                               params=params,
                                               total_tests=0,
                                               totals_by_result={},
                                               net_elapsed_time=0,
                                               has_finished=False)
    return execution_report


def _parse_execution_data(execution_directory=None, project=None, execution=None,
                          timestamp=None, finalize=False):
    execution_data = execution_report_default()

    if not execution_directory:
        execution_directory = execution_report_path(project, execution, timestamp)

    tests = []
    if os.path.isdir(execution_directory):
        tests = next(os.walk(execution_directory))[1]

    for test in tests:  # test_file + test set
        test_path = os.path.join(execution_directory, test)

        test_file_json_report = os.path.join(test_path, 'report.json')
        report_log_path = os.path.join(test_path, 'execution_info.log')

        if os.path.isfile(test_file_json_report):
            with open(test_file_json_report, encoding='utf-8') as f:
                # This contains one dict per test_function inside this test_file
                test_file_report = json.load(f)
        else:
            test_file_report = []

        for test_function in test_file_report:
            execution_data['total_tests'] += 1

            if finalize:
                if test_function['result'] == ResultsEnum.PENDING:
                    test_function['result'] = ResultsEnum.NOT_RUN

            _status_total = execution_data['totals_by_result'].get(test_function['result'], 0) + 1
            execution_data['totals_by_result'][test_function['result']] = _status_total
            execution_data['tests'].append(test_function)
    return execution_data


def get_execution_data(execution_directory=None, project=None, execution=None,
                       timestamp=None):
    """Retrieve the data of all the tests of an execution.

    From the report.json if it exists, otherwise it parses
    the tests one by one.

    The `report.json` should have been generated when the execution ended.
    """
    has_finished = False
    if execution_directory is None:
        execution_directory = execution_report_path(project, execution, timestamp)
    report_path = os.path.join(execution_directory, 'report.json')
    if os.path.isfile(report_path):
        with open(report_path, encoding='utf-8') as f:
            data = json.load(f)
            # if execution report file exists, the execution has finished
            has_finished = True
    else:
        data = _parse_execution_data(execution_directory, project, execution, timestamp)
    data['has_finished'] = has_finished
    return data


def generate_execution_report(execution_directory, elapsed_time, browsers, processes,
                              environments, tags, remote_url):
    """Generate execution json report.
    This is called at the end of the execution
    """
    data = _parse_execution_data(execution_directory=execution_directory, finalize=True)
    data['net_elapsed_time'] = elapsed_time
    data['params']['browsers'] = browsers
    remote_browser = any([b['capabilities'] for b in browsers])
    contains_remote = any('remote' in b['name'] for b in browsers)
    if remote_browser or contains_remote:
        data['params']['remote_url'] = remote_url
    data['params']['processes'] = processes
    data['params']['environments'] = environments
    data['params']['tags'] = tags
    data['has_finished'] = True
    report_path = os.path.join(execution_directory, 'report.json')
    with open(report_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)
    return data


def save_execution_json_report(report_data, reportdir, report_name='report'):
    """Save execution report data to the specified reportdir and report_name"""
    report_path = os.path.join(reportdir, f'{report_name}.json')
    if not os.path.exists(os.path.dirname(report_path)):
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=4, ensure_ascii=False)
    except IOError as e:
        if e.errno == errno.EACCES:
            print(f'ERROR: cannot write to {report_path}, PermissionError (Errno 13)')
        else:
            print(f'ERROR: There was an error writing to {report_path}')


def execution_report_path(project, execution, timestamp):
    return os.path.join(Project(project).report_directory_path, execution, timestamp)


def create_execution_directory(project, execution, timestamp):
    """Create the report directory for an execution.

    Directory should have the following path:
      <testdir>/projects/<project>/reports/<execution>/<timestamp>/
    """
    path = execution_report_path(project, execution, timestamp)
    os.makedirs(path, exist_ok=True)
    return path


def has_execution_finished(path):
    """Is a execution finished."""
    json_report_path = os.path.join(path, 'report.json')
    return os.path.isfile(json_report_path)


def test_file_execution_result_all_sets(project, execution, timestamp, test_file):
    """"""
    status = {
        'sets': {},
        'has_finished': False
    }
    path = execution_report_path(project, execution, timestamp)
    if os.path.isdir(path):
        set_dirs = [x for x in os.listdir(path) if os.path.isdir(os.path.join(path, x))]
        set_dirs = [x for x in set_dirs if x.startswith(test_file)]
        for set_dir in set_dirs:
            set_name = set_dir.replace(test_file, '')
            if set_name and set_name.startswith('.'):
                set_name = set_name[1:]
            test_file_report = test_report.get_test_file_report_json(project, execution, timestamp,
                                                                     test_file, set_name=set_name)
            log_info = test_report.get_test_info_log(project, execution, timestamp, test_file, set_name=set_name)
            log_debug = test_report.get_test_debug_log(project, execution, timestamp, test_file, set_name=set_name)
            if set_name == '':
                set_name = 'default'
            status['sets'][set_name] = {
                'report': test_file_report,
                'log_info': log_info,
                'log_debug': log_debug
            }
    status['has_finished'] = has_execution_finished(path)
    return status


def test_file_execution_result(project, execution, timestamp, test_file, set_name):
    all_sets = test_file_execution_result_all_sets(project, execution, timestamp, test_file)
    if set_name == '':
        set_name = 'default'
    return {
        'set': all_sets['sets'][set_name],
        'has_finished': all_sets['has_finished']
    }


def function_test_execution_result(project, execution, timestamp, test_file, test, set_name='',
                                   no_screenshots=False, encode_screenshots=False):
    """

    :Args:
      - encode_screenshots: return screenshot files encoded as a base64 string or
                            the screenshot filename (rel to its folder).
      - no_screenshots: convert screenshot values to None
    """
    path = execution_report_path(project, execution, timestamp)
    test_json = {
        'has_finished': False
    }
    if has_execution_finished(path):
        json_report = get_execution_data(path)
        for t in json_report['tests']:
            if t['test_file'] == test_file and t['test'] == test and t['set_name'] == set_name:
                test_json = t
                test_json['has_finished'] = True
                break
    else:
        test_json = test_report.get_test_function_report_json(project, execution, timestamp,
                                                              test_file, test, set_name)
        test_json['has_finished'] = False

    test_json['debug_log'] = test_report.get_test_debug_log(project, execution, timestamp,
                                                            test_file, set_name)
    test_json['info_log'] = test_report.get_test_info_log(project, execution, timestamp,
                                                          test_file, set_name)

    if no_screenshots:
        for step in test_json['steps']:
            step['screenshot'] = None
    elif encode_screenshots:
        for step in test_json['steps']:
            if step['screenshot'] is not None:
                image_filename = test_report.screenshot_path(project, execution, timestamp,
                                                             test_file, test, set_name,
                                                             step['screenshot'])
                b64 = base64.b64encode(open(image_filename, "rb").read()).decode('utf-8')
                step['screenshot'] = b64
    return test_json
