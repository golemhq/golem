"""Functions to parse Golem report files."""
import errno
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

from golem.core import session
from golem.test_runner.conf import ResultsEnum


def generate_junit_report(execution_directory, suite_name, timestamp,
                          report_folder=None, report_name=None):
    #DELETE
    from golem.report.execution_report import get_execution_data
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
