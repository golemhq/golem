import os

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

        exp = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<testsuites errors="1" failures="2" name="{suite_name}" tests="5" time="{time}">\n'
            '    <testsuite errors="1" failures="2" name="{suite_name}" skipped="1" tests="5" time="{time}" timestamp="{timestamp}">\n'
            '        <testcase classname="{cerror_cname}" name="code_error_test" time="{cerror_time}">\n'
            '            <error message="{cerror_msg}" type="code error"/>\n'
            '        </testcase>\n'
            '        <testcase classname="{error_cname}" name="error_test" time="{error_time}">\n'
            '            <failure message="{error_msg}" type="error"/>\n'
            '        </testcase>\n'
            '        <testcase classname="{failure_cname}" name="failure_test" time="{failure_time}">\n'
            '            <failure message="{failure_msg}" type="failure"/>\n'
            '        </testcase>\n'
            '        <testcase classname="{skip_cname}" name="skip_test" time="{skip_time}">\n'
            '            <skipped message="{skip_msg}" type="skipped"/>\n'
            '        </testcase>\n'
            '        <testcase classname="{success_cname}" name="success_test" time="{success_time}"/>\n'
            '    </testsuite>\n'
            '</testsuites>\n'
        )
        code_error_exec = [t for t in execution['exec_data']['tests'] if t['name'] == code_error_test][0]
        error_exec = [t for t in execution['exec_data']['tests'] if t['name'] == error_test][0]
        failure_exec = [t for t in execution['exec_data']['tests'] if t['name'] == failure_test][0]
        skip_exec = [t for t in execution['exec_data']['tests'] if t['name'] == skip_test][0]
        success_exec = [t for t in execution['exec_data']['tests'] if t['name'] == success_test][0]
        exp = exp.format(
            suite_name=execution['suite_name'],
            time=execution['exec_data']['net_elapsed_time'],
            timestamp=execution['timestamp'],
            cerror_cname='{}.{}'.format(code_error_exec['full_name'], code_error_exec['test_set']),
            cerror_time=code_error_exec['test_elapsed_time'],
            cerror_msg='{}',
            error_cname='{}.{}'.format(error_exec['full_name'], error_exec['test_set']),
            error_time=error_exec['test_elapsed_time'],
            error_msg='{}',
            failure_cname='{}.{}'.format(failure_exec['full_name'], failure_exec['test_set']),
            failure_time=failure_exec['test_elapsed_time'],
            failure_msg='{}',
            skip_cname='{}.{}'.format(skip_exec['full_name'], skip_exec['test_set']),
            skip_time=skip_exec['test_elapsed_time'],
            skip_msg='{}',
            success_cname='{}.{}'.format(success_exec['full_name'], success_exec['test_set']),
            success_time=success_exec['test_elapsed_time']
        )
        exp = exp.encode()

        assert xml == exp
        xml_path = os.path.join(execution['exec_dir'], 'report.xml')
        assert os.path.isfile(xml_path)