import json
import os


def get_date_time_from_timestamp(timestamp):
    sp = timestamp.split('.')
    date_time_string = '{0}/{1}/{2} {3}:{4}'.format(sp[0], sp[1], sp[2], sp[3], sp[4])
    return date_time_string


def get_last_executions(root_path, project=None, suite=None, limit=5):
    last_execution_data = {}

    path = os.path.join(root_path, 'projects')

    projects = []

    if project:
        projects = [project]
    else:
        projects = os.walk(path).__next__()[1]

    for project in projects:
        last_execution_data[project] = {}
        report_path = os.path.join(path, project, 'reports')
        executed_suites = []

        if suite:
            executed_suites = [suite]
        else:
            executed_suites = os.walk(report_path).__next__()[1]
            executed_suites = [x for x in executed_suites if x != 'single_tests']
            # if 'single_tests' in executed_suites:
            #     executed_suites.remove('single_tests')

        for exec_suite in executed_suites:
            last_execution_data[project][exec_suite] = []
            suite_executions = []
            suite_path = os.path.join(report_path, exec_suite)
            suite_executions = os.walk(suite_path).__next__()[1]
            last_executions = sorted(suite_executions)
            limit = int(limit)
            last_executions = last_executions[-limit:]
            for execution in last_executions:
                last_execution_data[project][exec_suite].append(execution)

    return last_execution_data


def _parse_execution_data(execution_directory=None, workspace=None,
                         project=None, suite=None, execution=None):
    execution_data = {
        'test_cases': [],
        'total_cases_ok': 0,
        'total_cases_fail': 0,
        'total_cases': 0,
        'total_pending': 0,
    }

    if not execution_directory:
        execution_directory = os.path.join(workspace, 'projects', project,
                                           'reports', suite, execution)

    test_cases = os.walk(execution_directory).__next__()[1]

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
            execution_data['total_cases'] += 1
            new_test_case['test_set'] = test_set
            module = ''
            sub_modules = []
            test_case_splitted = test_case.split('.')
            if len(test_case_splitted) > 1:
                module = test_case_splitted[0]
                if len(test_case_splitted) > 2:
                    sub_modules = test_case_splitted[1:-1]
            new_test_case['module'] = module
            test_case_name = test_case_splitted[-1]
            new_test_case['sub_modules'] = sub_modules
            new_test_case['name'] = test_case_name
            new_test_case['full_name'] = test_case

            test_set_path = os.path.join(test_case_path, test_set)

            # if the suite is being executed, the report dir might exist,
            # but the report.json may still not be generated
            report_json_path = os.path.join(test_set_path, 'report.json')

            # check if the test has finished
            if not os.path.exists(report_json_path):
                # test has not finished, add empty test case to the list
                new_test_case['result'] = 'pending'
                execution_data['test_cases'].append(new_test_case)
                execution_data['total_pending'] += 1

            else:
                # test has finished
                with open(os.path.join(test_set_path, 'report.json'), 'r') as json_file:
                    report_data = json.load(json_file)
                new_test_case['result'] = report_data['result']
                if report_data['result'] == 'pass':
                    execution_data['total_cases_ok'] += 1
                elif report_data['result'] == 'fail':
                    execution_data['total_cases_fail'] += 1
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

                execution_data['test_cases'].append(new_test_case)

    return execution_data


def get_execution_data(execution_directory=None, workspace=None,
                       project=None, suite=None, execution=None):
    """retrieve the data of all the tests of a suite execution.
    from the execution_report.json if it exists else it parses
    the tests one by one.
    when the suite ends, the execution_report.json is generated"""
    has_finished = False
    if execution_directory:
        report_path = os.path.join(execution_directory, 'execution_report.json')
    else:
        report_path = os.path.join(workspace, 'projects', project,
                                   'reports', suite, execution, 'execution_report.json')
    if os.path.exists(report_path):
        # get execution report
        with open(report_path) as json_file:
            data = json.load(json_file)
            has_finished = True
    else:
        data = _parse_execution_data(execution_directory, workspace,
                                     project, suite, execution)
    data['has_finished'] = has_finished
    return data


def get_test_case_data(root_path, project, test, suite=None, execution=None,
                       test_set=None, is_single=False):
    """ retrieves all the date of a single test case execution"""
    test_case_data = {
        'log': [],
    }
    if is_single:
        test_case_dir = os.path.join(root_path, 'projects', project, 'reports',
                                     'single_tests', test, execution, test_set)
    else:
        test_case_dir = os.path.join(root_path, 'projects', project, 'reports',
                                     suite, execution, test, test_set)
    report_json_path = os.path.join(test_case_dir, 'report.json')
    if os.path.exists(report_json_path):
        with open(report_json_path, 'r') as json_file:
            report_data = json.load(json_file)

            module = ''
            sub_modules = []
            test_case_splitted = test.split('.')
            if len(test_case_splitted) > 1:
                module = test_case_splitted[0]
                if len(test_case_splitted) > 2:
                    sub_modules = test_case_splitted[1:-1]
            test_case_data['module'] = module
            test_case_name = test_case_splitted[-1]
            test_case_data['sub_modules'] = sub_modules
            test_case_data['name'] = test_case_name
            test_case_data['full_name'] = test
            test_case_data['description'] = report_data['description']
            test_case_data['result'] = report_data['result']
            test_case_data['test_elapsed_time'] = report_data['test_elapsed_time']
            start_date_time = get_date_time_from_timestamp(report_data['test_timestamp'])
            test_case_data['start_date_time'] = start_date_time
            test_case_data['error'] = report_data['error']
            test_case_data['short_error'] = report_data['short_error']
            test_case_data['browser'] = report_data['browser']
            test_case_data['environment'] = report_data['environment']
            steps = []
            for step in report_data['steps']:
                if '__' in step:
                    this_step = {'message': step.split('__')[0],
                                 'screenshot': step.split('__')[1]}
                else:
                    this_step = {'message': step,
                                 'screenshot': None}
                steps.append(this_step)
            test_case_data['steps'] = steps

            test_case_data['test_set'] = test_set
            test_case_data['execution'] = execution
            test_case_data['data'] = report_data['test_data']
            if 'set_name' in report_data:
                test_case_data['set_name'] = report_data['set_name']

    log_path = os.path.join(test_case_dir, 'execution.log')
    if os.path.exists(log_path):
        with open(log_path, 'r') as log_file:
            log = log_file.readlines()
            test_case_data['log'] = log

    return test_case_data


def is_execution_finished(path, sets):
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
    """generate a json report of an entire suite execution so it is not
    needed to parse the entire execution each time it is requested"""
    data = _parse_execution_data(execution_directory=execution_directory)
    data['net_elapsed_time'] = elapsed_time
    report_path = os.path.join(execution_directory, 'execution_report.json')
    with open(report_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4)
