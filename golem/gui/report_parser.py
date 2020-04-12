"""Functions to parse Golem report files."""
import base64
import errno
import json
import os
import shutil
import sys
import traceback
import xml.etree.ElementTree as ET
from xml.dom import minidom

from golem.core import session, utils
from golem.test_runner.conf import ResultsEnum
from golem.core.project import Project


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


def get_date_time_from_timestamp(timestamp):
    """Get the date time from a timestamp.

    The timestamp must have the following format:
    'year.month.day.hour.minutes'
    Example:
    '2017.12.20.10.31' -> '2017/12/20 10:31'
    """
    date_time_string = timestamp
    sp = timestamp.split('.')
    if len(sp) >= 5:
        date_time_string = '{0}/{1}/{2} {3}:{4}'.format(sp[0], sp[1], sp[2], sp[3], sp[4])
    return date_time_string


# def get_last_executions(projects=None, suite=None, limit=5):
#     """Get the last n executions.
#
#     Get the executions of one suite or all the suites,
#     one project or all the projects.
#
#     Returns a list of executions (timestamps strings)
#     ordered in descendant order by execution time and
#     limited by `limit`
#     """
#     last_execution_data = {}
#     path = os.path.join(session.testdir, 'projects')
#     # if no projects provided, search every project
#     if not projects:
#         projects = next(os.walk(path))[1]
#     for project in projects:
#         last_execution_data[project] = {}
#         report_path = os.path.join(path, project, 'reports')
#         executed_suites = []
#         # use one suite or all the suites
#         if suite:
#             if os.path.isdir(os.path.join(report_path, suite)):
#                 executed_suites = [suite]
#         else:
#             executed_suites = next(os.walk(report_path))[1]
#             executed_suites = [x for x in executed_suites if x != 'single_tests']
#         for suite in executed_suites:
#             suite_path = os.path.join(report_path, suite)
#             suite_executions = next(os.walk(suite_path))[1]
#             last_executions = sorted(suite_executions)
#             limit = int(limit)
#             last_executions = last_executions[-limit:]
#             if len(last_executions):
#                 last_execution_data[project][suite] = last_executions
#     return last_execution_data


# def _parse_execution_data(execution_directory=None, project=None,
#                           suite=None, execution=None, finalize=False):
#     execution_data = get_execution_report_default()
#     if not execution_directory:
#         execution_directory = os.path.join(session.testdir, 'projects', project,
#                                            'reports', suite, execution)
#     tests = []
#     if os.path.isdir(execution_directory):
#         tests = next(os.walk(execution_directory))[1]
#
#     for test in tests:
#         # each test may have n >= 1 test sets
#         # each test set is considered a different test
#         test_path = os.path.join(execution_directory, test)
#         test_sets = os.walk(test_path).__next__()[1]
#
#         for test_set in test_sets:
#             new_test = {
#                 'test_set': '',
#                 'module': '',
#                 'sub_modules': '',
#                 'name': '',
#                 'full_name': '',
#                 'result': '',
#                 'test_elapsed_time': '',
#                 'start_date_time': '',
#                 'browser': '',
#                 'data': '',
#                 'environment': '',
#                 'set_name': ''
#             }
#             execution_data['total_tests'] += 1
#             new_test['test_set'] = test_set
#             module = ''
#             sub_modules = []
#             test_split = test.split('.')
#             if len(test_split) > 1:
#                 module = test_split[0]
#                 if len(test_split) > 2:
#                     sub_modules = test_split[1:-1]
#             new_test['module'] = module
#             test_name = test_split[-1]
#             new_test['sub_modules'] = sub_modules
#             new_test['name'] = test_name
#             new_test['full_name'] = test
#
#             test_set_path = os.path.join(test_path, test_set)
#             report_json_path = os.path.join(test_set_path, 'report.json')
#             report_log_path = os.path.join(test_set_path, 'execution_info.log')
#             try:
#                 with open(report_json_path) as f:
#                     report_data = json.load(f)
#                     status = report_data['result']
#                     new_test['test_elapsed_time'] = report_data['test_elapsed_time']
#                     start_date_time = get_date_time_from_timestamp(
#                         report_data['test_timestamp'])
#                     new_test['start_date_time'] = start_date_time
#                     new_test['browser'] = report_data['browser']
#                     new_test['data'] = report_data['test_data']
#                     new_test['environment'] = report_data['environment']
#                     # TODO, previous versions won't have set_name
#                     # remove the if when retro-compatibility is not required
#                     if 'set_name' in report_data:
#                         new_test['set_name'] = report_data['set_name']
#             except FileNotFoundError:
#                 if os.path.isfile(report_log_path):
#                     # test had been started
#                     status = ResultsEnum.STOPPED if finalize else ResultsEnum.RUNNING
#                 else:
#                     # test had not been started
#                     status = ResultsEnum.NOT_RUN if finalize else ResultsEnum.PENDING
#             except json.decoder.JSONDecodeError:
#                 # report.json exists but contains malformed JSON
#                 status = ResultsEnum.STOPPED if finalize else ResultsEnum.RUNNING
#             except Exception:
#                 sys.exit('an error occurred generating JSON report\n{}'
#                          .format(traceback.format_exc()))
#             new_test['result'] = status
#             _status_total = execution_data['totals_by_result'].get(status, 0) + 1
#             execution_data['totals_by_result'][status] = _status_total
#             execution_data['tests'].append(new_test)
#     return execution_data


# def get_execution_data(execution_directory=None, project=None, suite=None, execution=None):
#     """Retrieve the data of all the tests of a suite execution.
#
#     From the report.json if it exists, otherwise it parses
#     the tests one by one.
#
#     The `report.json` should be generated when the suite
#     execution ends.
#     """
#     has_finished = False
#     if execution_directory is None:
#         execution_directory = os.path.join(session.testdir, 'projects', project, 'reports',
#                                            suite, execution)
#     if os.path.isfile(os.path.join(execution_directory, 'report.json')):
#         with open(os.path.join(execution_directory, 'report.json')) as f:
#             data = json.load(f)
#             has_finished = True
#     elif os.path.isfile(os.path.join(execution_directory, 'execution_report.json')):
#         # backward compatibility
#         # TODO remove
#         with open(os.path.join(execution_directory, 'execution_report.json')) as f:
#             data = json.load(f)
#             has_finished = True
#     else:
#         data = _parse_execution_data(execution_directory, project, suite, execution)
#     data['has_finished'] = has_finished
#     return data


# def get_test_case_data(project, test, suite=None, execution=None, test_set=None,
#                        is_single=False, encode_screenshots=False, no_screenshots=False):
#     """Retrieves all the data of a single test execution.
#
#     :Args:
#       - encode_screenshots: return screenshot files encoded as a base64 string or
#                             the screenshot filename (rel to its folder).
#       - no_screenshots: convert screenshot values to None
#     """
#     # TODO execution and test_set are not optional
#     test_data = {
#         'module': '',
#         'sub_modules': '',
#         'name': '',
#         'full_name': '',
#         'description': '',
#         'result': '',
#         'test_elapsed_time': '',
#         'start_date_time': '',
#         'errors': [],
#         'browser': '',
#         'environment': '',
#         'steps': [],
#         'debug_log': [],
#         'info_log': [],
#         'has_finished': False
#     }
#     if is_single:
#         test_dir = os.path.join(session.testdir, 'projects', project, 'reports',
#                                 'single_tests', test, execution, test_set)
#     else:
#         test_dir = os.path.join(session.testdir, 'projects', project, 'reports',
#                                 suite, execution, test, test_set)
#     report_json_path = os.path.join(test_dir, 'report.json')
#     if os.path.isfile(report_json_path):
#         test_data['has_finished'] = True
#         with open(report_json_path, 'r') as json_file:
#             report_data = json.load(json_file)
#             module = ''
#             sub_modules = []
#             test_split = test.split('.')
#             if len(test_split) > 1:
#                 module = test_split[0]
#                 if len(test_split) > 2:
#                     sub_modules = test_split[1:-1]
#             test_data['module'] = module
#             test_name = test_split[-1]
#             test_data['sub_modules'] = sub_modules
#             test_data['name'] = test_name
#             test_data['full_name'] = test
#             test_data['description'] = report_data['description']
#             test_data['result'] = report_data['result']
#             test_data['test_elapsed_time'] = report_data['test_elapsed_time']
#             start_date_time = get_date_time_from_timestamp(report_data['test_timestamp'])
#             test_data['start_date_time'] = start_date_time
#             test_data['errors'] = report_data['errors']
#             test_data['browser'] = report_data['browser']
#             test_data['environment'] = report_data['environment']
#             test_data['steps'] = report_data['steps']
#             if no_screenshots:
#                 for step in test_data['steps']:
#                     step['screenshot'] = None
#             elif encode_screenshots:
#                 for step in test_data['steps']:
#                     if step['screenshot'] is not None:
#                         image_filename = os.path.join(test_dir, step['screenshot'])
#                         b64 = base64.b64encode(open(image_filename, "rb").read()).decode('utf-8')
#                         step['screenshot'] = b64
#             test_data['test_set'] = test_set
#             test_data['execution'] = execution
#             test_data['data'] = report_data['test_data']
#             if 'set_name' in report_data:
#                 test_data['set_name'] = report_data['set_name']
#
#     debug_log_path = os.path.join(test_dir, 'execution_debug.log')
#     info_log_path = os.path.join(test_dir, 'execution_info.log')
#     if os.path.isfile(debug_log_path):
#         with open(debug_log_path) as log_file:
#             log = log_file.readlines()
#             test_data['debug_log'] = log
#     if os.path.isfile(info_log_path):
#         with open(info_log_path) as log_file:
#             log = log_file.readlines()
#             test_data['info_log'] = log
#     return test_data


# def is_execution_finished(path, sets):
#     """Is a suite execution finished.
#
#     It is considered finished when all the tests contain
#     a `report.json` file
#     """
#     if sets:
#         is_finished = True
#         for data_set in sets:
#             report_path = os.path.join(path, data_set, 'report.json')
#             if not os.path.exists(report_path):
#                 is_finished = False
#     else:
#         is_finished = False
#     return is_finished


def generate_execution_report(execution_directory, elapsed_time, browsers,
                              processes, environments, tags, remote_url):
    """Generate a json report of the entire suite execution so
    it is not required to parse the entire execution test by test
    each time it is requested by the reports module."""
    # DELETE
    from golem.report.report import _parse_execution_data
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


def generate_junit_report(execution_directory, suite_name, timestamp,
                          report_folder=None, report_name=None):
    #DELETE
    from golem.report.report import get_execution_data
    data = get_execution_data(execution_directory=execution_directory)

    totals_by_result = data['totals_by_result']
    junit_errors = totals_by_result.get(ResultsEnum.CODE_ERROR, 0)
    junit_failure = (totals_by_result.get(ResultsEnum.FAILURE, 0) +
                     totals_by_result.get(ResultsEnum.ERROR, 0))
    testsuites_attrs = {
        'name': suite_name,
        'errors': str(junit_errors),
        'failures': str(junit_failure),
        'tests': str(data['total_tests']),
        'time': str(data['net_elapsed_time'])
    }
    testsuites = ET.Element('testsuites', testsuites_attrs)

    testsuites_attrs['timestamp'] = timestamp
    testsuite = ET.SubElement(testsuites, 'testsuite', testsuites_attrs)

    for test in data['tests']:
        # If the sets have names use them, otherwise use the generated name.
        set_name = test['set_name'] if test['set_name'] is not "" else test['test_set']
        test_attrs = {
            'name': test['full_name'],
            'classname': '{}.{}'.format(test['full_name'], set_name),
            'status': test['result'],
            'time': str(test['test_elapsed_time'])
        }
        testcase = ET.SubElement(testsuite, 'testcase', test_attrs)

        if test['result'] in (ResultsEnum.CODE_ERROR, ResultsEnum.FAILURE, ResultsEnum.ERROR):
            # JUnit has only two types of errors so we map 'code error' to error and 'failure' and 'error' to failure.
            error_type = 'error' if test['result'] == ResultsEnum.ERROR else 'failure'
            error_data = {
                'type': test['result'],
                'message': str(test['data'])
            }
            error_message = ET.SubElement(testcase, error_type, error_data)

    xmlstring = ET.tostring(testsuites)
    doc = minidom.parseString(xmlstring).toprettyxml(indent=' ' * 4, encoding='UTF-8')
    if not report_folder:
        report_folder = execution_directory
    if not report_name:
        report_name = 'report'

    report_path = os.path.join(report_folder, report_name + '.xml')
    if not os.path.exists(os.path.dirname(report_path)):
        os.makedirs(os.path.dirname(report_path), exist_ok=True)

    try:
        with open(report_path, 'w') as f:
            f.write(doc.decode('UTF-8'))
    except IOError as e:
        if e.errno == errno.EACCES:
            print('ERROR: cannot write to {}, PermissionError (Errno 13)'
                  .format(report_path))
        else:
            print('ERROR: There was an error writing to {}'.format(report_path))

    return doc


def get_or_generate_junit_report(project, suite, execution):
    """Get the HTML report as a string.
    If it does not exist, generate it:
    Report is generated at
    <testdir>/projects/<project>/reports/<suite>/<execution>/report.html|report-no-images.html
    """
    report_filename = 'report'
    report_directory = os.path.join(session.testdir, 'projects', project, 'reports',
                                    suite, execution)
    report_filepath = os.path.join(report_directory, report_filename + '.xml')
    if os.path.isfile(report_filepath):
        xml_string = open(report_filepath).read()
    else:
        xml_string = generate_junit_report(report_directory, suite, execution)
    return xml_string


# def delete_execution(project, suite, execution):
#     errors = []
#     path = suite_execution_path(project, suite, execution)
#     if os.path.isdir(path):
#         try:
#             shutil.rmtree(path)
#         except:
#             pass
#     return errors


# def suite_execution_path(project, suite, execution):
#     return os.path.join(Project(project).report_directory_path, suite, execution)
