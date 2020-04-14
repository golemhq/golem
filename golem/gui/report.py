"""Golem GUI Report blueprint"""
import json
import os

from flask import jsonify, render_template, Response, send_from_directory
from flask.blueprints import Blueprint
from flask_login import login_required

from golem.core import session, utils
from .gui_utils import project_exists, permission_required
from golem.gui.user_management import Permissions
from golem.report import execution_report as exec_report
from golem.report import test_report
from golem.report import junit_report
from golem.report import html_report


report_bp = Blueprint('report', __name__)


# REPORT DASHBOARD VIEW
@report_bp.route("/report/")
@login_required
def report_dashboard():
    return render_template('report/report_dashboard.html', project=None, suite=None)


# REPORT DASHBOARD PROJECT VIEW
@report_bp.route("/report/project/<project>/")
@login_required
@project_exists
@permission_required(Permissions.REPORTS_ONLY)
def report_dashboard_project(project):
    return render_template('report/report_dashboard.html', project=project, suite=None)


# REPORT DASHBOARD SUITE VIEW
@report_bp.route("/report/project/<project>/suite/<suite>/")
@login_required
@project_exists
@permission_required(Permissions.REPORTS_ONLY)
def report_dashboard_suite(project, suite):
    return render_template('report/report_dashboard.html', project=project, suite=suite)


# REPORT EXECUTION VIEW
@report_bp.route("/report/project/<project>/suite/<suite>/<execution>/")
@login_required
@project_exists
@permission_required(Permissions.REPORTS_ONLY)
def report_execution(project, suite, execution):
    formatted_date = utils.get_date_time_from_timestamp(execution)
    return render_template('report/report_execution.html', project=project, suite=suite,
                           execution=execution, execution_data=None,
                           formatted_date=formatted_date, static=False)


# REPORT EXECUTION VIEW STATIC HTML
@report_bp.route("/report/project/<project>/suite/<suite>/<execution>/html/")
@login_required
@project_exists
@permission_required(Permissions.REPORTS_ONLY)
def report_execution_static_html(project, suite, execution):
    html_report_string = html_report.get_or_generate_html_report(project, suite, execution)
    return html_report_string


# REPORT EXECUTION VIEW STATIC HTML DOWNLOAD
@report_bp.route("/report/project/<project>/suite/<suite>/<execution>/html/download/")
@login_required
@project_exists
@permission_required(Permissions.REPORTS_ONLY)
def report_execution_static_html_download(project, suite, execution):
    html_report_string = html_report.get_or_generate_html_report(project, suite, execution)
    headers = {'Content-disposition': 'attachment; filename={}'.format('report.html')}
    return Response(html_report_string, mimetype='text/html', headers=headers)


# REPORT EXECUTION VIEW STATIC HTML NO IMAGES
@report_bp.route("/report/project/<project>/suite/<suite>/<execution>/html-no-images/")
@login_required
@project_exists
@permission_required(Permissions.REPORTS_ONLY)
def report_execution_static_html_no_images(project, suite, execution):
    html_report_string = html_report.get_or_generate_html_report(project, suite, execution,
                                                               no_images=True)
    return html_report_string


# REPORT EXECUTION VIEW STATIC HTML NO IMAGES DOWNLOAD
@report_bp.route("/report/project/<project>/suite/<suite>/<execution>/html-no-images/download/")
@login_required
@project_exists
@permission_required(Permissions.REPORTS_ONLY)
def report_execution_static_html_no_images_download(project, suite, execution):
    html_report_string = html_report.get_or_generate_html_report(project, suite, execution,
                                                                 no_images=True)
    headers = {
        'Content-disposition': 'attachment; filename={}'.format('report-no-images.html')}
    return Response(html_report_string, mimetype='text/html', headers=headers)


# REPORT EXECUTION VIEW JUNIT
@report_bp.route("/report/project/<project>/suite/<suite>/<execution>/junit/")
@login_required
@project_exists
@permission_required(Permissions.REPORTS_ONLY)
def report_execution_junit(project, suite, execution):
    junit_report_string = junit_report.get_or_generate_junit_report(project, suite,
                                                                    execution)
    return Response(junit_report_string, mimetype='text/xml')


# REPORT EXECUTION VIEW JUNIT DOWNLOAD
@report_bp.route("/report/project/<project>/suite/<suite>/<execution>/junit/download/")
@login_required
@project_exists
@permission_required(Permissions.REPORTS_ONLY)
def report_execution_junit_download(project, suite, execution):
    junit_report_string = junit_report.get_or_generate_junit_report(project, suite,
                                                                    execution)
    headers = {'Content-disposition': 'attachment; filename={}'.format('report.xml')}
    return Response(junit_report_string, mimetype='text/xml', headers=headers)


# REPORT EXECUTION VIEW JSON
@report_bp.route("/report/project/<project>/suite/<suite>/<execution>/json/")
@login_required
@project_exists
@permission_required(Permissions.REPORTS_ONLY)
def report_execution_json(project, suite, execution):
    json_report = exec_report.get_execution_data(project=project, suite=suite, execution=execution)
    return jsonify(json_report)


# REPORT EXECUTION VIEW JSON DOWNLOAD
@report_bp.route("/report/project/<project>/suite/<suite>/<execution>/json/download/")
@login_required
@project_exists
@permission_required(Permissions.REPORTS_ONLY)
def report_execution_json_download(project, suite, execution):
    report_data = exec_report.get_execution_data(project=project, suite=suite,
                                                 execution=execution)
    json_report = json.dumps(report_data, indent=4)
    headers = {'Content-disposition': 'attachment; filename={}'.format('report.json')}
    return Response(json_report, mimetype='application/json', headers=headers)


# REPORT TEST VIEW
@report_bp.route("/report/project/<project>/<suite>/<execution>/<test>/<test_set>/")
@login_required
@project_exists
@permission_required(Permissions.REPORTS_ONLY)
def report_test(project, suite, execution, test, test_set):
    test_data = test_report.get_test_case_data(project, test, suite=suite, execution=execution,
                                               test_set=test_set, is_single=False)
    return render_template('report/report_test.html', project=project, suite=suite,
                           execution=execution, test_case=test, test_set=test_set,
                           test_case_data=test_data)


# REPORT TEST JSON VIEW
@report_bp.route("/report/project/<project>/<suite>/<execution>/<test>/<test_set>/json/")
@login_required
@project_exists
@permission_required(Permissions.REPORTS_ONLY)
def report_test_json(project, suite, execution, test, test_set):
    test_data = test_report.get_test_case_data(project, test, suite=suite, execution=execution,
                                               test_set=test_set, is_single=False)
    return jsonify(test_data)


# TEST SCREENSHOT
@report_bp.route('/report/screenshot/<project>/<suite>/<execution>/<test>/<test_set>/<scr>/')
@login_required
@project_exists
@permission_required(Permissions.REPORTS_ONLY)
def screenshot_file(project, suite, execution, test, test_set, scr):
    screenshot_path = os.path.join(session.testdir, 'projects', project,
                                   'reports', suite, execution, test, test_set)
    return send_from_directory(screenshot_path, scr)


# TEST SCREENSHOT
@report_bp.route('/test/screenshot/<project>/<test>/<execution>/<test_set>/<scr>/')
@login_required
@project_exists
@permission_required(Permissions.REPORTS_ONLY)
def screenshot_file2(project, test, execution, test_set, scr):
    screenshot_path = os.path.join(session.testdir, 'projects', project,
                                   'reports', 'single_tests', test, execution, test_set)
    return send_from_directory(screenshot_path, scr)
