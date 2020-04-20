import os
import errno
import xml.etree.ElementTree as ET
from xml.dom import minidom

from golem.test_runner.conf import ResultsEnum as Results
from golem.report.execution_report import get_execution_data
from golem.report.execution_report import suite_execution_path


def generate_junit_report(execution_directory, suite_name, timestamp, report_folder=None,
                          report_name=None):
    """Generate a report in JUnit XML format.

    Output conforms to https://github.com/jenkinsci/xunit-plugin/blob/master/
    src/main/resources/org/jenkinsci/plugins/xunit/types/model/xsd/junit-10.xsd
    """
    data = get_execution_data(execution_directory=execution_directory)

    totals = data['totals_by_result']
    errors = totals.get(Results.CODE_ERROR, 0)
    failures = totals.get(Results.FAILURE, 0) + totals.get(Results.ERROR, 0)
    skipped = totals.get(Results.SKIPPED, 0)

    testsuites_attrs = {
        'name': suite_name,
        'errors': str(errors),
        'failures': str(failures),
        'tests': str(data['total_tests']),
        'time': str(data['net_elapsed_time'])
    }
    testsuites = ET.Element('testsuites', testsuites_attrs)

    testsuites_attrs['timestamp'] = timestamp
    testsuites_attrs['skipped'] = str(skipped)
    testsuite = ET.SubElement(testsuites, 'testsuite', testsuites_attrs)

    for test in data['tests']:
        # If the sets have names use them, otherwise use the generated name.
        set_name = test['set_name'] if test['set_name'] is not "" else test['test_set']
        test_attrs = {
            'name': test['full_name'],
            'classname': '{}.{}'.format(test['full_name'], set_name),
            'time': str(test['test_elapsed_time'])
        }
        testcase = ET.SubElement(testsuite, 'testcase', test_attrs)

        # testcase nodes can contain 'failure', 'error', and 'skipped' sub-nodes
        # matching Golem 'error' and 'failure' to JUnit 'failure',
        # 'code error' to 'error', and 'skipped' to 'skipped'
        #
        # A Golem test can have 0 or more errors and 0 or 1 failures.
        # Correct mapping would be one sub-node for each of these.
        # The list of errors for a test is currently not available in the
        # execution json.
        if test['result'] in (Results.CODE_ERROR, Results.FAILURE, Results.ERROR, Results.SKIPPED):
            if test['result'] in [Results.ERROR, Results.FAILURE]:
                error_type = 'failure'
            elif test['result'] == Results.CODE_ERROR:
                error_type = 'error'
            else:
                error_type = 'skipped'
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


def get_or_generate_junit_report(project, suite, timestamp):
    """Get the JUnit XML report as a string.

    If it does not exist, generate it first.
    Report is generated at:
      <testdir>/projects/<project>/reports/<suite>/<execution>/report.xml
    """
    report_filename = 'report'
    report_directory = suite_execution_path(project, suite, timestamp)
    report_filepath = os.path.join(report_directory, report_filename + '.xml')
    if os.path.isfile(report_filepath):
        xml_string = open(report_filepath).read()
    else:
        xml_string = generate_junit_report(report_directory, suite, timestamp)
    return xml_string
