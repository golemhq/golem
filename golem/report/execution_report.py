import os
import json
import sys
import traceback
import errno

from golem.core import session, utils
from golem.test_runner.conf import ResultsEnum


def get_execution_report_default():
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


def _parse_execution_data(execution_directory=None, project=None,
                          suite=None, execution=None, finalize=False):
    execution_data = get_execution_report_default()
    if not execution_directory:
        execution_directory = os.path.join(session.testdir, 'projects', project,
                                           'reports', suite, execution)
    tests = []
    if os.path.isdir(execution_directory):
        tests = next(os.walk(execution_directory))[1]

    for test in tests:
        # each test may have n >= 1 test sets
        # each test set is considered a different test
        test_path = os.path.join(execution_directory, test)
        test_sets = os.walk(test_path).__next__()[1]

        for test_set in test_sets:
            new_test = {
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
            new_test['test_set'] = test_set
            module = ''
            sub_modules = []
            test_split = test.split('.')
            if len(test_split) > 1:
                module = test_split[0]
                if len(test_split) > 2:
                    sub_modules = test_split[1:-1]
            new_test['module'] = module
            test_name = test_split[-1]
            new_test['sub_modules'] = sub_modules
            new_test['name'] = test_name
            new_test['full_name'] = test

            test_set_path = os.path.join(test_path, test_set)
            report_json_path = os.path.join(test_set_path, 'report.json')
            report_log_path = os.path.join(test_set_path, 'execution_info.log')
            try:
                with open(report_json_path) as f:
                    report_data = json.load(f)
                    status = report_data['result']
                    new_test['test_elapsed_time'] = report_data['test_elapsed_time']
                    start_date_time = utils.get_date_time_from_timestamp(
                        report_data['test_timestamp'])
                    new_test['start_date_time'] = start_date_time
                    new_test['browser'] = report_data['browser']
                    new_test['data'] = report_data['test_data']
                    new_test['environment'] = report_data['environment']
                    # TODO, previous versions won't have set_name
                    # remove the if when retro-compatibility is not required
                    if 'set_name' in report_data:
                        new_test['set_name'] = report_data['set_name']
            except FileNotFoundError:
                if os.path.isfile(report_log_path):
                    # test had been started
                    status = ResultsEnum.STOPPED if finalize else ResultsEnum.RUNNING
                else:
                    # test had not been started
                    status = ResultsEnum.NOT_RUN if finalize else ResultsEnum.PENDING
            except json.decoder.JSONDecodeError:
                # report.json exists but contains malformed JSON
                status = ResultsEnum.STOPPED if finalize else ResultsEnum.RUNNING
            except Exception:
                sys.exit('an error occurred generating JSON report\n{}'
                         .format(traceback.format_exc()))
            new_test['result'] = status
            _status_total = execution_data['totals_by_result'].get(status, 0) + 1
            execution_data['totals_by_result'][status] = _status_total
            execution_data['tests'].append(new_test)
    return execution_data


def get_execution_data(execution_directory=None, project=None, suite=None,
                       execution=None):
    """Retrieve the data of all the tests of a suite execution.

    From the report.json if it exists, otherwise it parses
    the tests one by one.

    The `report.json` should be generated when the suite
    execution ends.
    """
    has_finished = False
    if execution_directory is None:
        execution_directory = os.path.join(session.testdir, 'projects', project,
                                           'reports', suite, execution)
    if os.path.isfile(os.path.join(execution_directory, 'report.json')):
        with open(os.path.join(execution_directory, 'report.json')) as f:
            data = json.load(f)
            has_finished = True
    elif os.path.isfile(os.path.join(execution_directory, 'execution_report.json')):
        # backward compatibility
        # TODO remove
        with open(os.path.join(execution_directory, 'execution_report.json')) as f:
            data = json.load(f)
            has_finished = True
    else:
        data = _parse_execution_data(execution_directory, project, suite, execution)
    data['has_finished'] = has_finished
    return data


def generate_execution_report(execution_directory, elapsed_time, browsers, processes,
                              environments, tags, remote_url):
    """Generate a json report of the entire suite execution so
    it is not required to parse the entire execution test by test
    each time it is requested by the reports module."""
    data = _parse_execution_data(execution_directory=execution_directory, finalize=True)
    data['net_elapsed_time'] = elapsed_time
    data['params']['browsers'] = browsers
    remote_browser = any([b['remote'] for b in browsers])
    contains_remote = any('remote' in b['name'] for b in browsers)
    if remote_browser or contains_remote:
        data['params']['remote_url'] = remote_url
    data['params']['processes'] = processes
    data['params']['environments'] = environments
    data['params']['tags'] = tags
    report_path = os.path.join(execution_directory, 'report.json')
    with open(report_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4)
    return data


def save_execution_json_report(report_data, reportdir, report_name='report'):
    """Save execution report data to the specified reportdir and name"""
    report_path = os.path.join(reportdir, '{}.json'.format(report_name))
    if not os.path.exists(os.path.dirname(report_path)):
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
    try:
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=4)
    except IOError as e:
        if e.errno == errno.EACCES:
            print('ERROR: cannot write to {}, PermissionError (Errno 13)'
                  .format(report_path))
        else:
            print('ERROR: There was an error writing to {}'.format(report_path))


def create_execution_directory(project, timestamp, test_name=None, suite_name=None):
    """Create directory to store report for suite or single test.

    If suite, directory will be:
    <testdir>/projects/<project>/reports/<suite_name>/<timestamp>/

    If test, directory will be:
    <testdir>/projects/<project>/reports/single_tests/<test_name>/<timestamp>/
    """
    if test_name:
        execution_directory = os.path.join(session.testdir, 'projects', project, 'reports',
                                           'single_tests', test_name, timestamp)
    elif suite_name:
        execution_directory = os.path.join(session.testdir, 'projects', project, 'reports',
                                           suite_name, timestamp)
    else:
        # TODO
        import sys
        sys.exit('Invalid params for create_test_execution_directory')

    if not os.path.isdir(execution_directory):
        try:
            os.makedirs(execution_directory)
        except:
            pass
    return execution_directory