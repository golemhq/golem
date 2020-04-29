import os

from golem.report import html_report


class TestGenerateHTMLReport:

    def test_generate_html_report(self, project_class, test_utils):
        _, project = project_class.activate()
        execution = test_utils.execute_random_suite(project)

        html = html_report.generate_html_report(project, execution['suite_name'], execution['timestamp'])

        html_path = os.path.join(execution['exec_dir'], 'report.html')
        assert os.path.isfile(html_path)
        with open(html_path, encoding='utf-8') as f:
            assert f.read() == html
