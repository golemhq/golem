"""Golem GUI Report blueprint"""
import json

from flask import jsonify, render_template, Response, send_from_directory
from flask.blueprints import Blueprint
from flask_login import login_required

from golem.core import utils
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
    return render_template('report/report_dashboard.html', project=None, execution=None)


# REPORT DASHBOARD PROJECT VIEW
@report_bp.route("/report/<project>/")
@login_required
@project_exists
@permission_required(Permissions.REPORTS_ONLY)
def report_dashboard_project(project):
    return render_template('report/report_dashboard.html', project=project, execution=None)


# REPORT DASHBOARD SUITE VIEW
@report_bp.route("/report/<project>/<execution>/")
@login_required
@project_exists
@permission_required(Permissions.REPORTS_ONLY)
def report_dashboard_suite(project, execution):
    return render_template('report/report_dashboard.html', project=project, execution=execution)


# OLD REPORT DASHBOARD PROJECT VIEW
@report_bp.route("/report-old/")
@report_bp.route("/report-old/<project>/")
@report_bp.route("/report-old/<project>/<execution>/")
@login_required
@permission_required(Permissions.REPORTS_ONLY)
def report_dashboard_old(project=None, execution=None):
    return render_template('report/report_dashboard_old.html', project=project, execution=execution)


# REPORT EXECUTION VIEW
@report_bp.route("/report/<project>/<execution>/<timestamp>/")
@login_required
@project_exists
@permission_required(Permissions.REPORTS_ONLY)
def report_execution(project, execution, timestamp):
    formatted_date = utils.get_date_time_from_timestamp(timestamp)
    return render_template('report/report_execution.html', project=project,
                           execution=execution, timestamp=timestamp, execution_data=None,
                           formatted_date=formatted_date, static=False)


# REPORT EXECUTION VIEW STATIC HTML
@report_bp.route("/report/<project>/<execution>/<timestamp>/html/")
@login_required
@project_exists
@permission_required(Permissions.REPORTS_ONLY)
def report_execution_static_html(project, execution, timestamp):
    return html_report.get_or_generate_html_report(project, execution, timestamp)


# REPORT EXECUTION VIEW STATIC HTML DOWNLOAD
@report_bp.route("/report/<project>/<execution>/<timestamp>/html/download/")
@login_required
@project_exists
@permission_required(Permissions.REPORTS_ONLY)
def report_execution_static_html_download(project, execution, timestamp):
    html_report_string = html_report.get_or_generate_html_report(project, execution, timestamp)
    headers = {'Content-disposition': 'attachment; filename=report.html'}
    return Response(html_report_string, mimetype='text/html', headers=headers)


# REPORT EXECUTION VIEW STATIC HTML NO IMAGES
@report_bp.route("/report/<project>/<execution>/<timestamp>/html-no-images/")
@login_required
@project_exists
@permission_required(Permissions.REPORTS_ONLY)
def report_execution_static_html_no_images(project, execution, timestamp):
    html_report_string = html_report.get_or_generate_html_report(
        project, execution, timestamp, no_images=True)
    return html_report_string


# REPORT EXECUTION VIEW STATIC HTML NO IMAGES DOWNLOAD
@report_bp.route("/report/<project>/<execution>/<timestamp>/html-no-images/download/")
@login_required
@project_exists
@permission_required(Permissions.REPORTS_ONLY)
def report_execution_static_html_no_images_download(project, execution, timestamp):
    html_report_string = html_report.get_or_generate_html_report(project, execution, timestamp,
                                                                 no_images=True)
    headers = {'Content-disposition': 'attachment; filename=report-no-images.html'}
    return Response(html_report_string, mimetype='text/html', headers=headers)


# REPORT EXECUTION VIEW JUNIT
@report_bp.route("/report/<project>/<execution>/<timestamp>/junit/")
@report_bp.route("/report/<project>/<execution>/<timestamp>/xml/")
@login_required
@project_exists
@permission_required(Permissions.REPORTS_ONLY)
def report_execution_junit(project, execution, timestamp):
    junit_report_string = junit_report.get_or_generate_junit_report(
        project, execution, timestamp)
    return Response(junit_report_string, mimetype='text/xml')


# REPORT EXECUTION VIEW JUNIT DOWNLOAD
@report_bp.route("/report/<project>/<execution>/<timestamp>/junit/download/")
@login_required
@project_exists
@permission_required(Permissions.REPORTS_ONLY)
def report_execution_junit_download(project, execution, timestamp):
    junit_report_string = junit_report.get_or_generate_junit_report(
        project, execution, timestamp)
    headers = {'Content-disposition': 'attachment; filename=report.xml'}
    return Response(junit_report_string, mimetype='text/xml', headers=headers)


# REPORT EXECUTION VIEW JSON
@report_bp.route("/report/<project>/<execution>/<timestamp>/json/")
@login_required
@project_exists
@permission_required(Permissions.REPORTS_ONLY)
def report_execution_json(project, execution, timestamp):
    json_report = exec_report.get_execution_data(project=project, execution=execution,
                                                 timestamp=timestamp)
    return json_report


# REPORT EXECUTION VIEW JSON DOWNLOAD
@report_bp.route("/report/<project>/<execution>/<timestamp>/json/download/")
@login_required
@project_exists
@permission_required(Permissions.REPORTS_ONLY)
def report_execution_json_download(project, execution, timestamp):
    report_data = exec_report.get_execution_data(project=project, execution=execution,
                                                 timestamp=timestamp)
    json_report = json.dumps(report_data, indent=4)
    headers = {'Content-disposition': 'attachment; filename=report.json'}
    return Response(json_report, mimetype='application/json', headers=headers)


# REPORT TEST FILE VIEW
@report_bp.route("/report/<project>/<execution>/<timestamp>/<test_file>/")
@report_bp.route("/report/<project>/<execution>/<timestamp>/<test_file>/<set_name>/")
@login_required
@project_exists
@permission_required(Permissions.REPORTS_ONLY)
def report_test(project, execution, timestamp, test_file, set_name=''):
    data = exec_report.test_file_execution_result(project, execution, timestamp, test_file, set_name)
    return render_template('report/report_test.html', project=project, execution=execution,
                           timestamp=timestamp, test_file=test_file, set_name=set_name,
                           test_data=data)


# REPORT TEST JSON VIEW
@report_bp.route("/report/<project>/<execution>/<timestamp>/<test_file>/json/")
@report_bp.route("/report/<project>/<execution>/<timestamp>/<test_file>/<set_name>/json/")
@login_required
@project_exists
@permission_required(Permissions.REPORTS_ONLY)
def report_test_json(project, execution, timestamp, test_file, set_name=''):
    data = exec_report.test_file_execution_result(project, execution, timestamp, test_file, set_name)
    return jsonify(data)


# TEST SCREENSHOT
@report_bp.route('/report/screenshot/<project>/<execution>/<timestamp>/<test_file>/<set_name>/<test>/<scr>/')
@login_required
@project_exists
@permission_required(Permissions.REPORTS_ONLY)
def screenshot_file(project, execution, timestamp, test_file, set_name, test, scr):
    if set_name == 'default':
        set_name = ''
    path = test_report.screenshot_dir(project, execution, timestamp, test_file, test, set_name)
    return send_from_directory(path, scr)
