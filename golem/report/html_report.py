import errno
import os

from flask import render_template

from golem.core import utils
from golem import gui
from golem.report import execution_report as exec_report


def generate_html_report(project, execution, timestamp, destination_folder=None,
                         report_name=None, no_images=False):
    """Generate static HTML report.
    Report is generated in <report_directory>/<report_name>
    By default it's generated in <testdir>/projects/<project>/reports/<suite>/<timestamp>
    Default name is 'report.html' and 'report-no-images.html'
    """
    execution_directory = exec_report.execution_report_path(project, execution, timestamp)

    if destination_folder is None:
        destination_folder = execution_directory

    if not report_name:
        if no_images:
            report_name = 'report-no-images'
        else:
            report_name = 'report'

    formatted_date = utils.get_date_time_from_timestamp(timestamp)
    app = gui.create_app()
    static_folder = app.static_folder
    # css paths
    css_folder = os.path.join(static_folder, 'css')
    boostrap_css = os.path.join(css_folder, 'bootstrap', 'bootstrap.min.css')
    main_css = os.path.join(css_folder, 'main.css')
    report_css = os.path.join(css_folder, 'report.css')
    # js paths
    js_folder = os.path.join(static_folder, 'js')
    main_js = os.path.join(js_folder, 'main.js')
    jquery_js = os.path.join(js_folder, 'external', 'jquery.min.js')
    datatables_js = os.path.join(js_folder, 'external', 'datatable', 'datatables.min.js')
    bootstrap_js = os.path.join(js_folder, 'external', 'bootstrap.min.js')
    report_execution_js = os.path.join(js_folder, 'report_execution.js')

    css = {
        'bootstrap': open(boostrap_css, encoding='utf-8').read(),
        'main': open(main_css, encoding='utf-8').read(),
        'report': open(report_css, encoding='utf-8').read()
    }
    js = {
        'jquery': open(jquery_js, encoding='utf-8').read(),
        'datatables': open(datatables_js, encoding='utf-8').read(),
        'bootstrap': open(bootstrap_js, encoding='utf-8').read(),
        'main': open(main_js, encoding='utf-8').read(),
        'report_execution': open(report_execution_js).read()
    }

    execution_data = exec_report.get_execution_data(execution_directory)
    detail_test_data = {}
    for test in execution_data['tests']:
        test_detail = exec_report.function_test_execution_result(
            project, execution, timestamp, test['test_file'], test['test'], test['set_name'],
            no_screenshots=no_images, encode_screenshots=True
        )
        # testId is test_file + test + set_name
        test_id = f"{test['test_file']}.{test['test']}"
        if test['set_name']:
            test_id = f"{test_id}.{test['set_name']}"
        detail_test_data[test_id] = test_detail
    with app.app_context():
        html_string = render_template(
            'report/report_execution_static.html', project=project, execution=execution,
            timestamp=timestamp, execution_data=execution_data,
            detail_test_data=detail_test_data, formatted_date=formatted_date,
            css=css, js=js, static=True
        )
    _, file_extension = os.path.splitext(report_name)
    if not file_extension:
        report_name = f'{report_name}.html'
    destination = os.path.join(destination_folder, report_name)

    if not os.path.exists(os.path.dirname(destination)):
        os.makedirs(os.path.dirname(destination), exist_ok=True)

    try:
        with open(destination, 'w', encoding='utf-8') as f:
            f.write(html_string)
    except IOError as e:
        if e.errno == errno.EACCES:
            print(f'ERROR: cannot write to {destination}, PermissionError (Errno 13)')
        else:
            print(f'ERROR: There was an error writing to {destination}')

    return html_string


def get_or_generate_html_report(project, execution, timestamp, no_images=False):
    """Get the HTML report as a string.
    If it does not exist, generate it:
    Report is generated at
    <testdir>/projects/<project>/reports/<execution>/<timestamp>/report.html|report-no-images.html
    """
    if no_images:
        report_filename = 'report-no-images'
    else:
        report_filename = 'report'

    report_directory = exec_report.execution_report_path(project, execution, timestamp)

    report_filepath = os.path.join(report_directory, report_filename + '.html')
    if os.path.isfile(report_filepath):
        html_string = open(report_filepath, encoding='utf-8').read()
    else:
        html_string = generate_html_report(project, execution, timestamp,
                                           report_name=report_filename,
                                           no_images=no_images)
    return html_string
