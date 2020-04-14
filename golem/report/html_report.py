import errno
import os

from flask import render_template

from golem.core import session, utils
from golem import gui
from golem.report import report
from golem.report import execution_report as exec_report
from golem.report import test_report


def generate_html_report(project, suite, execution, report_directory=None,
                         report_name=None, no_images=False):
    """Generate static HTML report.
    Report is generated in <report_directory>/<report_name>
    By default it's generated in <testdir>/projects/<project>/reports/<suite>/<timestamp>
    Default name is 'report.html' and 'report-no-images.html'
    """
    if not report_directory:
        report_directory = os.path.join(session.testdir, 'projects', project,
                                        'reports', suite, execution)
    if not report_name:
        if no_images:
            report_name = 'report-no-images'
        else:
            report_name = 'report'

    formatted_date = utils.get_date_time_from_timestamp(execution)
    app = gui.create_app()
    static_folder = app.static_folder
    css = {}
    js = {}
    boostrap_path = os.path.join(static_folder, 'css', 'bootstrap', 'bootstrap.min.css')
    datatables_js = os.path.join(static_folder, 'js', 'external', 'datatable', 'datatables.min.js')
    css['bootstrap'] = open(boostrap_path).read()
    css['main'] = open(os.path.join(static_folder, 'css', 'main.css')).read()
    css['report'] = open(os.path.join(static_folder, 'css', 'report.css')).read()
    js['jquery'] = open(os.path.join(static_folder, 'js', 'external', 'jquery.min.js')).read()
    js['datatables'] = open(datatables_js).read()
    js['bootstrap'] = open(os.path.join(static_folder, 'js', 'external', 'bootstrap.min.js')).read()
    js['main'] = open(os.path.join(static_folder, 'js', 'main.js')).read()
    js['report_execution'] = open(os.path.join(static_folder, 'js', 'report_execution.js')).read()
    execution_data = exec_report.get_execution_data(project=project, suite=suite, execution=execution)
    detail_test_data = {}
    for test in execution_data['tests']:
        test_detail = test_report.get_test_case_data(project, test['full_name'], suite=suite,
                                                     execution=execution, test_set=test['test_set'],
                                                     is_single=False, encode_screenshots=True,
                                                     no_screenshots=no_images)
        detail_test_data[test['test_set']] = test_detail
    with app.app_context():
        html_string = render_template('report/report_execution_static.html', project=project,
                                      suite=suite, execution=execution, execution_data=execution_data,
                                      detail_test_data=detail_test_data, formatted_date=formatted_date,
                                      css=css, js=js, static=True)
    _, file_extension = os.path.splitext(report_name)
    if not file_extension:
        report_name = '{}.html'.format(report_name)
    destination = os.path.join(report_directory, report_name)

    if not os.path.exists(os.path.dirname(destination)):
        os.makedirs(os.path.dirname(destination), exist_ok=True)

    try:
        with open(destination, 'w') as f:
            f.write(html_string)
    except IOError as e:
        if e.errno == errno.EACCES:
            print('ERROR: cannot write to {}, PermissionError (Errno 13)'
                  .format(destination))
        else:
            print('ERROR: There was an error writing to {}'.format(destination))

    return html_string


def get_or_generate_html_report(project, suite, execution, no_images=False):
    """Get the HTML report as a string.
    If it does not exist, generate it:
    Report is generated at
    <testdir>/projects/<project>/reports/<suite>/<execution>/report.html|report-no-images.html
    """
    if no_images:
        report_filename = 'report-no-images'
    else:
        report_filename = 'report'
    report_directory = os.path.join(session.testdir, 'projects', project,
                                    'reports', suite, execution)
    report_filepath = os.path.join(report_directory, report_filename + '.html')
    if os.path.isfile(report_filepath):
        html_string = open(report_filepath).read()
    else:
        html_string = generate_html_report(project, suite, execution,
                                           report_directory=report_directory,
                                           report_name=report_filename,
                                           no_images=no_images)
    return html_string
