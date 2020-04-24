import os
import xml.etree.ElementTree as ET

from golem.report.junit_report import generate_junit_report


class TestGenerateJunitReport:

    def test_generate_junit_report(self, project_class, test_utils):
        _, project = project_class.activate()
        success_test = 'foo.success_test'
        failure_test = 'bar.failure_test'
        error_test = 'error_test'
        code_error_test = 'code_error_test'
        skip_test = 'skip_test'
        test_utils.create_test(project, success_test)
        test_utils.create_failure_test(project, failure_test)
        test_utils.create_error_test(project, error_test)
        test_utils.create_code_error_test(project, code_error_test)
        test_utils.create_skip_test(project, skip_test)
        test_utils.create_suite(project, 'suite_one',
                                tests=[success_test, failure_test, error_test, code_error_test, skip_test])
        execution = test_utils.execute_suite(project, 'suite_one', ignore_sys_exit=True)

        xml = generate_junit_report(project, execution['suite_name'], execution['timestamp'])

        tests = execution['exec_data']['tests']
        code_error_exec = next(t for t in tests if t['full_name'] == code_error_test)
        error_exec = next(t for t in tests if t['full_name'] == error_test)
        failure_exec = next(t for t in tests if t['full_name'] == failure_test)
        skip_exec = next(t for t in tests if t['full_name'] == skip_test)
        success_exec = next(t for t in tests if t['full_name'] == success_test)
        xml = ET.fromstring(xml)
        # testsuites
        assert xml.tag == 'testsuites'
        assert xml.attrib == {
            'errors': '1',
            'failures': '2',
            'name': 'suite_one',
            'tests': '5',
            'time': str(execution['exec_data']['net_elapsed_time'])
        }
        assert len(xml) == 1
        # testsuites/testsuite
        testsuite = xml[0]
        assert testsuite.tag == 'testsuite'
        assert testsuite.attrib == {
            'errors': '1',
            'failures': '2',
            'name': 'suite_one',
            'skipped': '1',
            'tests': '5',
            'time': str(execution['exec_data']['net_elapsed_time']),
            'timestamp': execution['timestamp']
        }
        assert len(testsuite) == 5
        # testsuites/testsuite/code_error_test
        test = next(test for test in testsuite if test.attrib['classname'] == code_error_test)
        assert test.attrib == {
            'classname': code_error_exec['full_name'],
            'name': code_error_exec['test_set'],
            'time': str(code_error_exec['test_elapsed_time'])
        }
        assert len(test) == 2
        # testsuites/testsuite/code_error_test/error
        error = next(node for node in test if node.tag == 'error')
        assert error.tag == 'error'
        assert error.attrib == {
            'type': 'code error',
            'message': '{}'
        }
        # testsuites/testsuite/code_error_test/system-out
        system_out = next(node for node in test if node.tag == 'system-out')
        assert 'INFO Browser: chrome' in system_out.text
        assert 'INFO Test Result: CODE ERROR' in system_out.text
        # testsuites/testsuite/error_test
        test = next(test for test in testsuite if test.attrib['classname'] == error_test)
        assert test.attrib == {
            'classname': error_exec['full_name'],
            'name': error_exec['test_set'],
            'time': str(error_exec['test_elapsed_time'])
        }
        assert len(test) == 2
        # testsuites/testsuite/error_test/failure
        failure = next(node for node in test if node.tag == 'failure')
        assert failure.tag == 'failure'
        assert failure.attrib == {
            'type': 'error',
            'message': '{}'
        }
        # testsuites/testsuite/failure_test
        test = next(test for test in testsuite if test.attrib['classname'] == failure_test)
        assert test.attrib == {
            'classname': failure_exec['full_name'],
            'name': failure_exec['test_set'],
            'time': str(failure_exec['test_elapsed_time'])
        }
        assert len(test) == 2
        # testsuites/testsuite/failure_test/failure
        failure = next(node for node in test if node.tag == 'failure')
        assert failure.tag == 'failure'
        assert failure.attrib == {
            'type': 'failure',
            'message': '{}'
        }
        # testsuites/testsuite/skipped_test
        test = next(test for test in testsuite if test.attrib['classname'] == skip_test)
        assert test.attrib == {
            'classname': skip_exec['full_name'],
            'name': skip_exec['test_set'],
            'time': str(skip_exec['test_elapsed_time'])
        }
        assert len(test) == 2
        # testsuites/testsuite/skipped_test/skipped
        skipped = next(node for node in test if node.tag == 'skipped')
        assert skipped.tag == 'skipped'
        assert skipped.attrib == {
            'type': 'skipped',
            'message': '{}'
        }
        # testsuites/testsuite/success_test
        test = next(test for test in testsuite if test.attrib['classname'] == success_test)
        assert test.attrib == {
            'classname': success_exec['full_name'],
            'name': success_exec['test_set'],
            'time': str(success_exec['test_elapsed_time'])
        }
        assert len(test) == 1
        # testsuites/testsuite/success_test/system-out
        system_out = next(node for node in test if node.tag == 'system-out')
        assert 'INFO Browser: chrome' in system_out.text
        assert 'INFO Test Result: SUCCESS' in system_out.text

        xml_path = os.path.join(execution['exec_dir'], 'report.xml')
        assert os.path.isfile(xml_path)
