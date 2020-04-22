import os
import xml.etree.ElementTree as ET

from golem.report.junit_report import generate_junit_report


class TestGenerateJunitReport:

    def test_generate_junit_report(self, project_class, test_utils):
        _, project = project_class.activate()
        success_test = 'success_test'
        failure_test = 'failure_test'
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

        xml = generate_junit_report(execution['exec_dir'], execution['suite_name'], execution['timestamp'])

        tests = execution['exec_data']['tests']
        code_error_exec = next(t for t in tests if t['name'] == code_error_test)
        error_exec = next(t for t in tests if t['name'] == error_test)
        failure_exec = next(t for t in tests if t['name'] == failure_test)
        skip_exec = next(t for t in tests if t['name'] == skip_test)
        success_exec = next(t for t in tests if t['name'] == success_test)
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
        test = next(test for test in testsuite if test.attrib['name'] == code_error_test)
        assert test.attrib == {
            'classname': '{}.{}'.format(code_error_exec['full_name'], code_error_exec['test_set']),
            'name': 'code_error_test',
            'time': str(code_error_exec['test_elapsed_time'])
        }
        assert len(test) == 1
        # testsuites/testsuite/code_error_test/error
        error = test[0]
        assert error.tag == 'error'
        assert error.attrib == {
            'type': 'code error',
            'message': '{}'
        }
        # testsuites/testsuite/error_test
        test = next(test for test in testsuite if test.attrib['name'] == error_test)
        assert test.attrib == {
            'classname': '{}.{}'.format(error_exec['full_name'], error_exec['test_set']),
            'name': error_test,
            'time': str(error_exec['test_elapsed_time'])
        }
        assert len(test) == 1
        # testsuites/testsuite/error_test/failure
        failure = test[0]
        assert failure.tag == 'failure'
        assert failure.attrib == {
            'type': 'error',
            'message': '{}'
        }
        # testsuites/testsuite/failure_test
        test = next(test for test in testsuite if test.attrib['name'] == failure_test)
        assert test.attrib == {
            'classname': '{}.{}'.format(failure_exec['full_name'], failure_exec['test_set']),
            'name': failure_test,
            'time': str(error_exec['test_elapsed_time'])
        }
        assert len(test) == 1
        # testsuites/testsuite/failure_test/failure
        failure = test[0]
        assert failure.tag == 'failure'
        assert failure.attrib == {
            'type': 'failure',
            'message': '{}'
        }
        # testsuites/testsuite/skipped_test
        test = next(test for test in testsuite if test.attrib['name'] == skip_test)
        assert test.attrib == {
            'classname': '{}.{}'.format(skip_exec['full_name'], skip_exec['test_set']),
            'name': skip_test,
            'time': str(skip_exec['test_elapsed_time'])
        }
        assert len(test) == 1
        # testsuites/testsuite/skipped_test/skipped
        skipped = test[0]
        assert skipped.tag == 'skipped'
        assert skipped.attrib == {
            'type': 'skipped',
            'message': '{}'
        }
        # testsuites/testsuite/success_test
        test = next(test for test in testsuite if test.attrib['name'] == success_test)
        assert test.attrib == {
            'classname': '{}.{}'.format(success_exec['full_name'], success_exec['test_set']),
            'name': success_test,
            'time': str(success_exec['test_elapsed_time'])
        }
        assert len(test) == 0

        xml_path = os.path.join(execution['exec_dir'], 'report.xml')
        assert os.path.isfile(xml_path)
