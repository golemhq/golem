import os
import json
import errno

from golem.core import utils
from golem.core.project import Project


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
            new_test_function = test_function
            execution_data['total_tests'] += 1
            status = test_function['result']

            # except FileNotFoundError:
            #     if os.path.isfile(report_log_path):
            #         # test had been started
            #         status = ResultsEnum.STOPPED if finalize else ResultsEnum.RUNNING
            #     else:
            #         # test had not been started
            #         status = ResultsEnum.NOT_RUN if finalize else ResultsEnum.PENDING
            # except json.decoder.JSONDecodeError:
            #     # report.json exists but contains malformed JSON
            #     status = ResultsEnum.STOPPED if finalize else ResultsEnum.RUNNING
            # except Exception:
            #     sys.exit('an error occurred generating JSON report\n{}'
            #              .format(traceback.format_exc()))
            # new_test_function['result'] = status
            _status_total = execution_data['totals_by_result'].get(status, 0) + 1
            execution_data['totals_by_result'][status] = _status_total
            execution_data['tests'].append(new_test_function)
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
    remote_browser = any([b['remote'] for b in browsers])
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
    report_path = os.path.join(reportdir, '{}.json'.format(report_name))
    if not os.path.exists(os.path.dirname(report_path)):
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=4, ensure_ascii=False)
    except IOError as e:
        if e.errno == errno.EACCES:
            print('ERROR: cannot write to {}, PermissionError (Errno 13)'
                  .format(report_path))
        else:
            print('ERROR: There was an error writing to {}'.format(report_path))


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
