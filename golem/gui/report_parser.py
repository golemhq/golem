"""Functions to parse Golem report files."""
import json
import os
import base64

from golem.core import test_execution
from golem.test_runner.conf import ResultsEnum


def get_date_time_from_timestamp(timestamp):
    """Get the date time from a timestamp.

    The timestamp must have the following format:
    'year.month.day.hour.minutes'
    Example:
    '2017.12.20.10.31' -> '2017/12/20 10:31'
    """
    sp = timestamp.split('.')
    date_time_string = '{0}/{1}/{2} {3}:{4}'.format(sp[0], sp[1], sp[2], sp[3], sp[4])
    return date_time_string


def get_last_executions(root_path, projects=None, suite=None, limit=5):
    """Get the last n executions.
    
    Get the executions of one suite or all the suites,
    one project or all the projects.
    
    Returns a list of executions (timestamps strings)
    ordered in descendant order by execution time and
    limited by `limit`
    """
    last_execution_data = {}
    path = os.path.join(root_path, 'projects')
    # if no projects provided, search every project
    if not projects:
        projects = os.walk(path).__next__()[1]
    for project in projects:
        last_execution_data[project] = {}
        report_path = os.path.join(path, project, 'reports')
        # use one suite or all the suites
        if suite:
            executed_suites = [suite]
        else:
            executed_suites = os.walk(report_path).__next__()[1]
            executed_suites = [x for x in executed_suites if x != 'single_tests']
        for exec_suite in executed_suites:
            last_execution_data[project][exec_suite] = []
            suite_path = os.path.join(report_path, exec_suite)
            suite_executions = os.walk(suite_path).__next__()[1]
            last_executions = sorted(suite_executions)
            limit = int(limit)
            last_executions = last_executions[-limit:]
            for execution in last_executions:
                last_execution_data[project][exec_suite].append(execution)
    return last_execution_data


def _parse_execution_data(execution_directory=None, workspace=None, project=None,
                          suite=None, execution=None):
    execution_data = {
        'tests': [],
        'total_tests': 0,
        'totals_by_result': {}
    }
    if not execution_directory:
        execution_directory = os.path.join(workspace, 'projects', project,
                                           'reports', suite, execution)
    test_cases = []
    if os.path.isdir(execution_directory):
        test_cases = next(os.walk(execution_directory))[1]
    for test_case in test_cases:
        # each test case may have n >= 1 test sets
        # each test set is considered a different test
        test_case_path = os.path.join(execution_directory, test_case)
        test_sets = os.walk(test_case_path).__next__()[1]

        for test_set in test_sets:
            new_test_case = {
                'test_set': '',
                'module': '',
                'sub_modules': '',
                'name': '',
                'full_name': '',
                'result': '',
                'test_elapsed_time': '',
                'start_date_time': '',
                'browser': '',
                'data': '',
                'environment': '',
                'set_name': ''
            }
            execution_data['total_tests'] += 1
            new_test_case['test_set'] = test_set
            module = ''
            sub_modules = []
            test_case_split = test_case.split('.')
            if len(test_case_split) > 1:
                module = test_case_split[0]
                if len(test_case_split) > 2:
                    sub_modules = test_case_split[1:-1]
            new_test_case['module'] = module
            test_case_name = test_case_split[-1]
            new_test_case['sub_modules'] = sub_modules
            new_test_case['name'] = test_case_name
            new_test_case['full_name'] = test_case

            test_set_path = os.path.join(test_case_path, test_set)

            # if the suite is being executed, the report dir might exist,
            # but the report.json may still not be generated
            # check if the test has finished (report.json file exists)
            report_json_path = os.path.join(test_set_path, 'report.json')
            if not os.path.isfile(report_json_path):
                # test has not finished, add empty test case to the list (pending or running)
                status = ResultsEnum.PENDING
                report_log_path = os.path.join(test_set_path, 'execution_info.log')
                if os.path.isfile(report_log_path):
                    status = ResultsEnum.RUNNING
                new_test_case['result'] = status
                execution_data['tests'].append(new_test_case)
                execution_data['totals_by_result']['pending'] = execution_data['totals_by_result'].get('pending', 0) + 1
            else:
                # test has finished
                with open(os.path.join(test_set_path, 'report.json'), 'r') as json_file:
                    report_data = json.load(json_file)
                new_test_case['result'] = report_data['result']
                status = report_data['result']
                execution_data['totals_by_result'][status] = execution_data['totals_by_result'].get(status, 0) + 1
                new_test_case['test_elapsed_time'] = report_data['test_elapsed_time']
                start_date_time = get_date_time_from_timestamp(report_data['test_timestamp'])
                new_test_case['start_date_time'] = start_date_time
                new_test_case['browser'] = report_data['browser']
                new_test_case['data'] = report_data['test_data']
                new_test_case['environment'] = report_data['environment']
                # TODO, previous versions won't have set_name
                # remove the if when retro-compatibility is not required
                if 'set_name' in report_data:
                    new_test_case['set_name'] = report_data['set_name']
                execution_data['tests'].append(new_test_case)
    return execution_data


def get_execution_data(execution_directory=None, workspace=None,
                       project=None, suite=None, execution=None):
    """Retrieve the data of all the tests of a suite execution.
    
    From the execution_report.json if it exists, otherwise it parses
    the tests one by one.
    
    The `execution_report.json` should be generated when the suite
    execution ends.
    """
    has_finished = False
    if execution_directory:
        report_path = os.path.join(execution_directory, 'execution_report.json')
    else:
        report_path = os.path.join(workspace, 'projects', project,
                                   'reports', suite, execution,
                                   'execution_report.json')
    if os.path.exists(report_path):
        # get execution_report.json data
        with open(report_path) as json_file:
            data = json.load(json_file)
            has_finished = True
    else:
        # execution_report.json does not exist
        data = _parse_execution_data(execution_directory, workspace,
                                     project, suite, execution)
    data['has_finished'] = has_finished
    return data


def get_test_case_data(root_path, project, test, suite=None, execution=None,
                       test_set=None, is_single=False, encode_screenshots=False,
                       no_screenshots=False):
    """Retrieves all the data of a single test case execution.

    :Args:
      - encode_screenshots: return screenshot files encoded as a base64 string or
                            the screenshot filename (rel to its folder).
      - no_screenshots: convert screenshot values to None
    """
    # TODO execution and test_set are not optional
    test_case_data = {
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
        test_case_dir = os.path.join(root_path, 'projects', project, 'reports',
                                     'single_tests', test, execution, test_set)
    else:
        test_case_dir = os.path.join(root_path, 'projects', project, 'reports',
                                     suite, execution, test, test_set)
    report_json_path = os.path.join(test_case_dir, 'report.json')
    if os.path.isfile(report_json_path):
        test_case_data['has_finished'] = True
        with open(report_json_path, 'r') as json_file:
            report_data = json.load(json_file)
            module = ''
            sub_modules = []
            test_case_split = test.split('.')
            if len(test_case_split) > 1:
                module = test_case_split[0]
                if len(test_case_split) > 2:
                    sub_modules = test_case_split[1:-1]
            test_case_data['module'] = module
            test_case_name = test_case_split[-1]
            test_case_data['sub_modules'] = sub_modules
            test_case_data['name'] = test_case_name
            test_case_data['full_name'] = test
            test_case_data['description'] = report_data['description']
            test_case_data['result'] = report_data['result']
            test_case_data['test_elapsed_time'] = report_data['test_elapsed_time']
            start_date_time = get_date_time_from_timestamp(report_data['test_timestamp'])
            test_case_data['start_date_time'] = start_date_time
            test_case_data['errors'] = report_data['errors']
            test_case_data['browser'] = report_data['browser']
            test_case_data['environment'] = report_data['environment']
            test_case_data['steps'] = report_data['steps']
            if no_screenshots:
                for step in test_case_data['steps']:
                    step['screenshot'] = None
            elif encode_screenshots:
                for step in test_case_data['steps']:
                    if step['screenshot'] is not None:
                        image_filename = os.path.join(test_case_dir, step['screenshot'])
                        b64 = base64.b64encode(open(image_filename, "rb").read()).decode('utf-8')
                        step['screenshot'] = b64
            test_case_data['test_set'] = test_set
            test_case_data['execution'] = execution
            test_case_data['data'] = report_data['test_data']
            if 'set_name' in report_data:
                test_case_data['set_name'] = report_data['set_name']

    debug_log_path = os.path.join(test_case_dir, 'execution_debug.log')
    info_log_path = os.path.join(test_case_dir, 'execution_info.log')
    if os.path.isfile(debug_log_path):
        with open(debug_log_path) as log_file:
            log = log_file.readlines()
            test_case_data['debug_log'] = log
    if os.path.isfile(info_log_path):
        with open(info_log_path) as log_file:
            log = log_file.readlines()
            test_case_data['info_log'] = log
    return test_case_data


def is_execution_finished(path, sets):
    """Is a suite execution finished.

    It is considered finished when all the tests contain
    a `report.json` file
    """
    if sets:
        is_finished = True
        for data_set in sets:
            report_path = os.path.join(path, data_set, 'report.json')
            if not os.path.exists(report_path):
                is_finished = False
    else:
        is_finished = False
    return is_finished


def generate_execution_report(execution_directory, elapsed_time):
    """Generate a json report of the entire suite execution so
    it is not required to parse the entire execution test by test
    each time it is requested by the reports module."""
    data = _parse_execution_data(execution_directory=execution_directory)
    data['net_elapsed_time'] = elapsed_time
    report_path = os.path.join(execution_directory, 'execution_report.json')
    with open(report_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4)

