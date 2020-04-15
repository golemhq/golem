import os

from golem.report.junit_report import generate_junit_report


class TestGenerateJunitReport:

    def test_generate_junit_report(self, project_class, test_utils):
        _, project = project_class.activate()
        execution = test_utils.execute_random_suite(project)

        xml = generate_junit_report(execution['exec_dir'], execution['suite_name'], execution['timestamp'])

        suite_name = execution['suite_name']
        suite_time = execution['exec_data']['net_elapsed_time']
        timestamp = execution['timestamp']
        test_name = execution['exec_data']['tests'][0]['name']
        test_set = execution['exec_data']['tests'][0]['test_set']
        test_time = execution['exec_data']['tests'][0]['test_elapsed_time']
        class_name = '{}.{}'.format(test_name, test_set)
        expected = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                    '<testsuites errors="0" failures="0" name="{0}" tests="1" time="{1}">\n'
                    '    <testsuite errors="0" failures="0" name="{0}" tests="1" time="{1}" timestamp="{2}">\n'
                    '        <testcase classname="{3}" name="{4}" status="success" time="{5}"/>\n'
                    '    </testsuite>\n'
                    '</testsuites>\n'.format(suite_name, suite_time, timestamp, class_name, test_name, test_time).encode())
        assert xml == expected
        xml_path = os.path.join(execution['exec_dir'], 'report.xml')
        assert os.path.isfile(xml_path)
