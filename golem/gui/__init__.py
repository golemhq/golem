"""The Golem GUI application using Flask."""
import time
import json
import os
from urllib.parse import urlparse, urljoin

from flask import (abort, Flask, g, jsonify, redirect, render_template, request,
                   Response, send_from_directory, url_for)
from flask_login import (current_user, login_user, login_required,
                         LoginManager, logout_user)

from golem.core import (environment_manager, file_manager, lock, page_object,
                        settings_manager, test_case, test_execution, utils)
from golem.core import test_data as test_data_module
from golem.core import suite as suite_module

from . import gui_utils, report_parser, user
from .gui_utils import (project_exists, gui_permissions_required,
                        report_permissions_required)

app = Flask(__name__)

app.secret_key = '57095311a5465e90837d64f6e29bca0a'
app.config['SESSION_TYPE'] = 'filesystem'

login_manager = LoginManager()
login_manager.init_app(app)

root_path = None


# LOGIN VIEW
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        errors = []
        user_data = {}
        username = request.form['username']
        password = request.form['password']
        next_url = request.form['next']
        if not username:
            errors.append('Username is required')
        elif not password:
            errors.append('Password is required')
        else:
            user_data = user.get_user_data(username=username)
            if user_data is None:
                errors.append('Username does not exists')
            elif user_data['password'] != password:
                errors.append('Username and password do not match')
        if len(errors):
            return render_template('login.html', next_url=next_url, errors=errors)
        else:
            usr = user.User(user_data['id'], user_data['username'],
                            user_data['is_admin'], user_data['gui_projects'],
                            user_data['report_projects'])
            login_user(usr)
            if not next_url or not is_safe_url(next_url):
                next_url = '/'
            return redirect(next_url)
    else:
        next_url = request.args.get('next')
        if not next_url or not is_safe_url(next_url):
            next_url = '/'
        return render_template('login.html', next_url=next_url, errors=[])


# INDEX VIEW
@app.route("/")
@login_required
def index():
    """If user is admin or has '*' in report permissions they will
    have access to every project. Otherwise limit the project
    list to gui_permissions
    """
    if current_user.is_admin or '*' in current_user.gui_permissions:
        projects = utils.get_projects(test_execution.root_path)
    else:
        projects = current_user.gui_permissions
    return render_template('index.html', projects=projects)


# PROJECT VIEW - redirect to to /project/suites/
@app.route("/project/<project>/")
@login_required
@project_exists
@gui_permissions_required
def project_view(project):
    return redirect('/project/{}/suites/'.format(project))


# PROJECT TESTS VIEW
@app.route("/project/<project>/tests/")
@login_required
@project_exists
@gui_permissions_required
def project_tests(project):
    return render_template('project/project_tests.html', project=project)


# PROJECT SUITES VIEW
@app.route("/project/<project>/suites/")
@login_required
@project_exists
@gui_permissions_required
def project_suites(project):
    return render_template('project/project_suites.html', project=project)


# PROJECT PAGES VIEW
@app.route("/project/<project>/pages/")
@login_required
@project_exists
@gui_permissions_required
def project_pages(project):
    return render_template('project/project_pages.html', project=project)


# TEST CASE VIEW
@app.route("/project/<project>/test/<test_case_name>/")
@login_required
@project_exists
@gui_permissions_required
def test_case_view(project, test_case_name):
    # check if the file is locked
    # is_locked_by = lock.is_file_locked(root_path, project, test_case_name)
    # print(is_locked_by, g.user.username)
    # if is_locked_by and is_locked_by != g.user.username:
    #     abort(404, 'This file is locked by someone else.')
    # else:
    test_exists = test_case.test_case_exists(test_execution.root_path, project,
                                             test_case_name)
    if not test_exists:
        abort(404, 'The test {} does not exist'.format(test_case_name))
    tc_name, parents = utils.separate_file_from_parents(test_case_name)
    path = test_case.generate_test_case_path(root_path, project, test_case_name)
    _, error = utils.import_module(path)
    if error:
        url = url_for('test_case_code_view', project=project, test_case_name=test_case_name)
        content = ('<h4>There are errors in the test</h4>'
                   '<p>There are errors and the test cannot be displayed, '
                   'open the test code editor to solve them.</p>'
                   '<a class="btn btn-default" href="{}">Open Test Code</a>'
                   .format(url))
        return render_template('common_element_error.html', project=project,
                               item_name=test_case_name, content=content)
    else:
        test_case_contents = test_case.get_test_case_content(root_path, project,
                                                             test_case_name)
        test_data = test_data_module.get_test_data(root_path, project, test_case_name,
                                                   repr_strings=True)
        return render_template('test_builder/test_case.html', project=project,
                               test_case_contents=test_case_contents,
                               test_case_name=tc_name,
                               full_test_case_name=test_case_name,
                               test_data=test_data)


# TEST CASE CODE VIEW
@app.route("/project/<project>/test/<test_case_name>/code/")
@login_required
@project_exists
@gui_permissions_required
def test_case_code_view(project, test_case_name):
    test_exists = test_case.test_case_exists(test_execution.root_path, project,
                                             test_case_name)
    if not test_exists:
        abort(404, 'The test {} does not exist'.format(test_case_name))
    tc_name, parents = utils.separate_file_from_parents(test_case_name)
    path = os.path.join(test_execution.root_path, 'projects', project,
                        'tests', os.sep.join(parents), tc_name + '.py')
    test_case_contents = test_case.get_test_case_code(path)
    _, error = utils.import_module(path)
    external_data = test_data_module.get_external_test_data(root_path, project,
                                                            test_case_name)
    test_data_setting = test_execution.settings['test_data']
    return render_template('test_builder/test_case_code.html', project=project, 
                           test_case_contents=test_case_contents, test_case_name=tc_name,
                           full_test_case_name=test_case_name, test_data=external_data,
                           test_data_setting=test_data_setting, error=error)


# PAGE OBJECT VIEW
@app.route("/project/<project>/page/<full_page_name>/")
@login_required
@project_exists
@gui_permissions_required
def page_view(project, full_page_name, no_sidebar=False):
    path = page_object.generate_page_path(root_path, project, full_page_name)
    page_exists_ = page_object.page_exists(test_execution.root_path, project,
                                           full_page_name)
    if not page_exists_:
        abort(404, 'The page {} does not exist'.format(full_page_name))
    _, error = utils.import_module(path)
    if error:
        if no_sidebar:
            url = url_for('page_code_view_no_sidebar', project=project, full_page_name=full_page_name)
        else:
            url = url_for('page_code_view', project=project, full_page_name=full_page_name)
        content = ('<h4>There are errors in the page</h4>'
                   '<p>There are errors and the page cannot be displayed, '
                   'open the page code editor to solve them.</p>'
                   '<a class="btn btn-default" href="{}">Open Page Code</a>'
                   .format(url))
        return render_template('common_element_error.html', project=project,
                               item_name=full_page_name, content=content,
                               no_sidebar=no_sidebar)
    else:
        page_data = page_object.get_page_object_content(project, full_page_name)
        return render_template('page_builder/page_object.html',
                               project=project,
                               page_object_data=page_data,
                               page_name=full_page_name, 
                               no_sidebar=no_sidebar)


# PAGE OBJECT VIEW no sidebar
@app.route("/project/<project>/page/<full_page_name>/no_sidebar/")
@login_required
def page_view_no_sidebar(project, full_page_name):
    return page_view(project=project, full_page_name=full_page_name, no_sidebar=True)


# PAGE OBJECT CODE VIEW
@app.route("/project/<project>/page/<full_page_name>/code/")
@login_required
@project_exists
@gui_permissions_required
def page_code_view(project, full_page_name, no_sidebar=False):
    page_exists_ = page_object.page_exists(test_execution.root_path, project,
                                           full_page_name)
    if not page_exists_:
        abort(404, 'The page {} does not exist'.format(full_page_name))
    path = page_object.generate_page_path(root_path, project, full_page_name)
    _, error = utils.import_module(path)
    page_object_code = page_object.get_page_object_code(path)
    return render_template('page_builder/page_object_code.html', project=project,
                           page_object_code=page_object_code, page_name=full_page_name,
                           error=error, no_sidebar=no_sidebar)


# PAGE OBJECT CODE VIEW no sidebar
@app.route("/project/<project>/page/<full_page_name>/no_sidebar/code/")
@login_required
def page_code_view_no_sidebar(project, full_page_name):
    return page_code_view(project=project, full_page_name=full_page_name, no_sidebar=True)


# SUITE VIEW
@app.route("/project/<project>/suite/<suite>/")
@login_required
@project_exists
@gui_permissions_required
def suite_view(project, suite):
    suite_exists = suite_module.suite_exists(test_execution.root_path, project, suite)
    if not suite_exists:
        abort(404, 'The suite {} does not exist'.format(suite))
    all_test_cases = utils.get_test_cases(root_path, project)
    selected_tests = suite_module.get_suite_test_cases(root_path, project, suite)
    worker_amount = suite_module.get_suite_amount_of_workers(root_path, project, suite)
    browsers = suite_module.get_suite_browsers(root_path, project, suite)
    browsers = ', '.join(browsers)
    default_browser = test_execution.settings['default_browser']
    environments = suite_module.get_suite_environments(root_path, project, suite)
    environments = ', '.join(environments)
    return render_template('suite.html', project=project,
                           all_test_cases=all_test_cases['sub_elements'],
                           selected_tests=selected_tests, suite=suite,
                           worker_amount=worker_amount, browsers=browsers,
                           default_browser=default_browser, environments=environments)


# GLOBAL SETTINGS VIEW
@app.route("/settings/")
@login_required
def global_settings():
    settings = settings_manager.get_global_settings_as_string(root_path)
    return render_template('settings.html', project=None, global_settings=settings,
                           settings=None)


# PROJECT SETTINGS VIEW
@app.route("/project/<project>/settings/")
@login_required
@project_exists
@gui_permissions_required
def project_settings(project):
    gsettings = settings_manager.get_global_settings_as_string(root_path)
    psettings = settings_manager.get_project_settings_as_string(root_path, project)
    return render_template('settings.html', project=project, global_settings=gsettings,
                           settings=psettings)


# ENVIRONMENTS VIEW
@app.route("/project/<project>/environments/")
@login_required
@project_exists
@gui_permissions_required
def environments_view(project):
    data = environment_manager.get_environments_as_string(root_path, project)
    return render_template('environments.html', project=project, environment_data=data)


# LOGOUT VIEW
@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect('/')


########
# REPORT
########

# REPORT DASHBOARD VIEW
@app.route("/report/")
@login_required
def report_dashboard():
    """If user is admin or has '*' in report permissions they will
    have access to every project report. Otherwise limit the project
    list to report_permissions"""
    if current_user.is_admin or '*' in current_user.report_permissions:
        projects = utils.get_projects(test_execution.root_path)
    else:
        projects = current_user.report_permissions
    return render_template('report/report_dashboard.html', projects=projects,
                           project=None, suite='')


# REPORT DASHBOARD PROJECT VIEW
@app.route("/report/project/<project>/")
@login_required
@project_exists
@report_permissions_required
def report_dashboard_project(project):
    return render_template('report/report_dashboard.html', projects=[project],
                           project=project, suite='')


# REPORT DASHBOARD SUITE VIEW
@app.route("/report/project/<project>/suite/<suite>/")
@login_required
@project_exists
@report_permissions_required
def report_dashboard_suite(project, suite):
    return render_template('report/report_dashboard.html', projects=[project],
                           project=project, suite=suite)


# REPORT EXECUTION VIEW
@app.route("/report/project/<project>/suite/<suite>/<execution>/")
@login_required
@project_exists
@report_permissions_required
def report_execution(project, suite, execution):
    formatted_date = report_parser.get_date_time_from_timestamp(execution)
    return render_template('report/report_execution.html', project=project, suite=suite,
                           execution=execution, formatted_date=formatted_date)


# REPORT TEST VIEW
@app.route("/report/project/<project>/<suite>/<execution>/<test>/<test_set>/")
@login_required
@project_exists
@report_permissions_required
def report_test(project, suite, execution, test, test_set):
    test_case_data = report_parser.get_test_case_data(root_path, project, test,
                                                      suite=suite, execution=execution,
                                                      test_set=test_set, is_single=False)
    return render_template('report/report_test.html', project=project, suite=suite,
                           execution=execution, test_case=test, test_set=test_set,
                           test_case_data=test_case_data)


# TEST SCREENSHOT
@app.route('/report/screenshot/<project>/<suite>/<execution>/<test>/<test_set>/<scr>/')
@login_required
@project_exists
@report_permissions_required
def screenshot_file(project, suite, execution, test, test_set, scr):
    screenshot_path = os.path.join(test_execution.root_path, 'projects', project,
                                   'reports', suite, execution, test, test_set)
    return send_from_directory(screenshot_path, scr)


# TEST SCREENSHOT
@app.route('/test/screenshot/<project>/<test>/<execution>/<test_set>/<scr>/')
def screenshot_file2(project, test, execution, test_set, scr):
    screenshot_path = os.path.join(test_execution.root_path, 'projects', project,
                                   'reports', 'single_tests', test, execution, test_set)
    return send_from_directory(screenshot_path, scr)


# GENERATE HTML REPORT FILE
@app.route("/getHTMLReport")
def getHTMLReport():
    project = request.args.get('project')
    suite = request.args.get('suite')
    execution = request.args.get('execution')

    execution_data = report_parser.get_execution_data(workspace=root_path,
                                                      project=project,
                                                      suite=suite,
                                                      execution=execution)

    total_cases = execution_data['total_tests']
    total_cases_ok = execution_data['totals_by_result']['success']
    total_cases_fail = total_cases - total_cases_ok
    net_elapsed_time = execution_data['net_elapsed_time']
    total_time = 0
    for test in execution_data['tests']:
        total_time += test['test_elapsed_time']

    project_title = '' + project + ' - ' + suite + ''
    formatted_date = report_parser.get_date_time_from_timestamp(execution)

    okPercentage = total_cases_ok * 100 / total_cases
    failPercentage = total_cases_fail * 100 / total_cases + okPercentage

    main_css = open(os.path.join(os.path.dirname(__file__), "static/css/main.css"), 'r').read()
    main_js = open(os.path.join(os.path.dirname(__file__), "static/js/main.js"), 'r').read()
    report_css = open(os.path.join(os.path.dirname(__file__), "static/css/report.css"), 'r').read()

    bootstrap_css = open(os.path.join(os.path.dirname(__file__), "static/css/bootstrap/bootstrap.min.css"), 'r').read()
    bootstrap_theme_css = open(os.path.join(os.path.dirname(__file__), "static/css/bootstrap/bootstrap-theme.min.css"),
                               'r').read()
    jquery_js = open(os.path.join(os.path.dirname(__file__), "static/js/external/jquery.min.js"), 'r').read()
    bootstrap_js = open(os.path.join(os.path.dirname(__file__), "static/js/external/bootstrap.min.js"), 'r').read()

    report_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>{bootstrap_css}</style>
        <style>{bootstrap_theme_css}</style>
        <style>{main_css}</style>
        <style>{report_css}</style>

        <script>{jquery_js}</script>
        <script>{bootstrap_js}</script>
        <script>{main_js}</script>

    </head>
    <body>
        <div id="content" class="container-fluid">
            <div class="content-wrapper">
                <h2 style="display:inline-block;">{project_title} <small>({formatted_date})</small></h2>
            </div>
            <div class="col-md-12 project-container">
            <h3 class="no-margin-top">General</h3>
            <div class="widget widget-table">
                <div class="widget-content">
                    <div class="table-responsive">
                        <table id="generalTable" class="table general-table margin-bottom-5">
                            <thead>
                                <tr>
                                    <th>Module</th>
                                    <th>Total Tests</th>
                                    <th>Tests OK</th>
                                    <th>Tests Failed</th>
                                    <th>Percentage</th>
                                    <th>Total Time</th>
                                    <th>Net Time</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr class="total-row general-table-row cursor-pointer">
                                    <td class="module"></td>
                                    <td class="total-tests">{total_cases}</td>
                                    <td class="tests-ok">{total_cases_ok}</td>
                                    <td class="tests-failed">{total_cases_fail}</td>
                                    <td class="percentage">
                                        <div class="progress">
                                            <div aria-valuenow="10" style="width: 100%;" class="progress-bar pending pending-grey-background" data-transitiongoal="10"></div>
                                            <div aria-valuenow="10" style="width: 0%;" class="progress-bar fail-bar failed-red-background" data-transitiongoal="10"></div>
                                            <div aria-valuenow="20" style="width: 0%;" class="progress-bar ok-bar passed-green-background" data-transitiongoal="20"></div>
                                        </div>
                                    </td>
                                    <td class="total-time"></td>
                                    <td class="net-time"></td>
                                </tr>
                                <tr class="total-row general-table-row cursor-pointer">
                                    <td class="module">Total</td>
                                    <td class="total-tests">{total_cases}</td>
                                    <td class="tests-ok">{total_cases_ok}</td>
                                    <td class="tests-failed">{total_cases_fail}</td>
                                    <td class="percentage">
                                        <div class="progress">
                                            <div aria-valuenow="10" style="width: 100%;" class="progress-bar pending pending-grey-background" data-transitiongoal="10"></div>
                                            <div aria-valuenow="10" style="width: 0%;" class="progress-bar fail-bar failed-red-background" data-transitiongoal="10"></div>
                                            <div aria-valuenow="20" style="width: 0%;" class="progress-bar ok-bar passed-green-background" data-transitiongoal="20"></div>
                                        </div>
                                    </td>
                                    <td class="total-time">{total_time}</td>
                                    <td class="net-time">{net_time}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            <h3 class="no-margin-top">Detail</h3>
            <div class="widget widget-table">
                        <div class="widget-content">
                                <div class="table-responsive">
                                        <table id="detailTable" class="table detail-table margin-bottom-5">
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>Module</th>
                                    <th>Test Name</th>
                                    <th>Set Name</th>
                                    <th>Environment</th>
                                    <th>Browser</th>
                                    <th>Result</th>
                                    <th>Time</th>
                                    <th>&nbsp;</th>
                                </tr>
                            </thead>
                            <tbody>""".format(
        bootstrap_css=bootstrap_css,
        bootstrap_theme_css=bootstrap_theme_css,
        main_css=main_css,
        report_css=report_css,
        jquery_js=jquery_js,
        bootstrap_js=bootstrap_js,
        main_js=main_js,
        project_title=project_title,
        total_cases=total_cases,
        total_cases_ok=total_cases_ok,
        total_cases_fail=total_cases_fail,
        total_time=time.strftime('%Mm %Ss', time.gmtime(total_time)),
        net_time=time.strftime('%Mm %Ss', time.gmtime(net_elapsed_time)),
        formatted_date=formatted_date
    )

    count = 0
    for test in execution_data['tests']:
        test_name = test['name']
        test_folder = test['test_set']
        test_environment = test['environment']
        test_full_name = test['full_name']
        test_module = test['module']
        test_browser = test['browser']
        test_result = test['result']
        test_set_name = test['set_name']
        test_start_date_time = test['start_date_time']
        test_sub_modules = test['sub_modules']
        test_test_elapsed_time = test['test_elapsed_time']
        test_case_data = report_parser.get_test_case_data(root_path, project, test_full_name,
                                                          suite=suite, execution=execution,
                                                          test_set=test_folder, is_single=False)

        file_name = os.path.join(root_path, 'projects', project, 'reports', suite, execution, test_full_name,
                                 test['test_set'])

        test_case_steps = report_parser.return_html_test_steps(test_case_data, file_name)

        if test_result == 'success':
            pass_or_fail = """<span class="passed-green" style="font-size: 20px"><strong>&#9745;</strong></span>"""
        else:
            pass_or_fail = """<span class="failed-red" style="font-size: 20px"><strong>&#9746;</strong></span></span>"""

        report_html += """
            <tr>
                <td>
                    {count_plus_one}
                </td>
                <td>{test_module}</td>
                <td>{test_full_name}</td>
                <td>{test_set_name}</td>
                <td>{test_environment}</td>
                <td>{test_browser}</td>
                <td>{pass_or_fail} {test_result}</td>
                <td>{test_test_elapsed_time}</td>
                <td class="link">
                    <a href="javascript:;" data-toggle="collapse" data-target="#{test_full_name_css}_{count}" aria-expanded="false" aria-controls="{test_full_name_css}_{count}">
                        <span style="font-size: 20px"><strong>&#8853;</strong></span>
                    </a>
                </td>
            </tr>
            <tr style="height:0px !important;">
                <td style="height:0px !important; padding-top:0px !important; padding-bottom: 0px !important;"colspan="9">
                    <div class="collapse" id="{test_full_name_css}_{count}">
                        <div class="row">
                            <ol>
                                {test_case_steps}
                            </ol>
                        </div>
                    </div>
                </td>
            </tr>""".format(
                count_plus_one=count+1,
                test_module=test_module,
                test_full_name=test_full_name,
                test_set_name=test_set_name,
                test_environment=test_environment,
                test_browser=test_browser,
                pass_or_fail=pass_or_fail,
                test_result=test_result,
                test_test_elapsed_time=test_test_elapsed_time,
                test_full_name_css=test_full_name.replace('.', '-'),
                count=count,
                test_case_steps=test_case_steps)
        count += 1

    report_html += """
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    </div>
    <script>
        utils.animateProgressBar($('.fail-bar'), {failPercentage});
        utils.animateProgressBar($('.ok-bar'), {okPercentage});
    </script>
    </body>
    </html>
    """.format(failPercentage=failPercentage, okPercentage=okPercentage)

    return Response(report_html,
                    mimetype="text/html",
                    headers={
                        "Content-disposition": "attachment; "
                                               "filename=%s" % suite + '_report.html'
                    })

###############
# END OF REPORT
###############


#####
# API
#####


@app.route("/project/get_tests/", methods=['POST'])
@login_required
def get_tests():
    if request.method == 'POST':
        project = request.form['project']
        tests = utils.get_test_cases(root_path, project)
        return json.dumps(tests)


@app.route("/project/get_pages/", methods=['POST'])
@login_required
def get_pages():
    if request.method == 'POST':
        project = request.form['project']
        pages = utils.get_pages(root_path, project)
        return json.dumps(pages)


@app.route("/project/get_suites/", methods=['POST'])
@login_required
def get_suite():
    if request.method == 'POST':
        project = request.form['project']
        suites = utils.get_suites(root_path, project)
        return json.dumps(suites)


@app.route("/delete_element/", methods=['POST'])
@login_required
def delete_element():
    if request.method == 'POST':
        project = request.form['project']
        elem_type = request.form['elemType']
        full_path = request.form['fullPath']
        errors = utils.delete_element(root_path, project, elem_type, full_path)
        return json.dumps(errors)


@app.route("/duplicate_element/", methods=['POST'])
@login_required
def duplicate_element():
    if request.method == 'POST':
        project = request.form['project']
        elem_type = request.form['elemType']
        full_path = request.form['fullPath']
        new_file_full_path = request.form['newFileFullPath']
        errors = utils.duplicate_element(root_path, project, elem_type,
                                         full_path, new_file_full_path)
        return json.dumps(errors)


@app.route("/rename_element/", methods=['POST'])
@login_required
def rename_element():
    if request.method == 'POST':
        project = request.form['project']
        elem_type = request.form['elemType']
        full_filename = request.form['fullFilename']
        new_full_filename = request.form['newFullFilename']

        error = ''

        old_filename, old_parents = utils.separate_file_from_parents(full_filename)
        new_filename, new_parents = utils.separate_file_from_parents(new_full_filename)

        if len(new_filename) == 0:
            error = 'File name cannot be empty'
        else:
            for c in new_full_filename.replace('.', ''):
                if not c.isalnum() and c not in ['-', '_']:
                    error = 'Only letters, numbers, \'-\' and \'_\' are allowed'
                    break

        dir_type_name = ''
        if not error:
            if elem_type == 'test':
                dir_type_name = 'tests'
            elif elem_type == 'page':
                dir_type_name = 'pages'
            elif elem_type == 'suite':
                dir_type_name = 'suites'
            
            old_path = os.path.join(root_path, 'projects', project, dir_type_name,
                                    os.sep.join(old_parents))
            new_path = os.path.join(root_path, 'projects', project, dir_type_name,
                                    os.sep.join(new_parents))
            error = file_manager.rename_file(old_path, old_filename+'.py',
                                             new_path, new_filename+'.py')
        if not error and elem_type == 'test':
            # try to rename data file in /data/ folder
            # TODO, data files in /data/ will be deprecated
            old_path = os.path.join(root_path, 'projects', project, 'data',
                                    os.sep.join(old_parents))
            new_path = os.path.join(root_path, 'projects', project, 'data',
                                    os.sep.join(new_parents))
            if os.path.isfile(os.path.join(old_path, old_filename+'.csv')):
                error = file_manager.rename_file(old_path, old_filename+'.csv',
                                                 new_path, new_filename+'.csv')
            # try to rename data file in /tests/ folder
            old_path = os.path.join(root_path, 'projects', project, 'tests',
                                    os.sep.join(old_parents))
            new_path = os.path.join(root_path, 'projects', project, 'tests',
                                    os.sep.join(new_parents))
            if os.path.isfile(os.path.join(old_path, old_filename+'.csv')):
                error = file_manager.rename_file(old_path, old_filename+'.csv',
                                                 new_path, new_filename+'.csv')
        return json.dumps(error)


@app.route("/get_page_objects/", methods=['POST'])
@login_required
def get_page_objects():
    if request.method == 'POST':
        project = request.form['project']
        path = page_object.pages_base_dir(root_path, project)
        page_objects = file_manager.get_files_dot_path(path, extension='.py')
        return json.dumps(page_objects)


@app.route("/get_selected_page_object_elements/", methods=['POST'])
@login_required
def get_selected_page_object_elements():
    if request.method == 'POST':
        project = request.form['project']
        page_name = request.form['pageObject']
        result = {
            'error': None,
            'content': []
        }
        if not page_object.page_exists(root_path, project, page_name):
            result['error'] = 'page does not exist'
        else:
            result['content'] = page_object.get_page_object_content(project, page_name)
        return json.dumps(result)


@app.route("/new_tree_element/", methods=['POST'])
@login_required
def new_tree_element():
    if request.method == 'POST':
        project = request.form['project']
        elem_type = request.form['elementType']
        is_dir = json.loads(request.form['isDir'])
        full_path = request.form['fullPath']
        add_parents = request.form['addParents']
        full_path = full_path.replace(' ', '_')
        dot_path = full_path
        errors = []
        full_path = full_path.split('.')
        element_name = full_path.pop()
        parents = full_path
        # verify that the string only contains letters, numbers
        # dashes or underscores
        for c in element_name:
            if not c.isalnum() and c not in ['-', '_']:
                errors.append('Only letters, numbers, \'-\' and \'_\' are allowed')
                break
        if not errors:
            if elem_type == 'test':
                if is_dir:
                    errors = file_manager.new_directory_of_type(root_path, project,
                                                                parents, element_name,
                                                                dir_type='tests')
                else:
                    errors = test_case.new_test_case(root_path, project,
                                                     parents, element_name)
            elif elem_type == 'page':
                if is_dir:
                    errors = file_manager.new_directory_of_type(root_path, project,
                                                                parents, element_name,
                                                                dir_type='pages')
                else:
                    errors = page_object.new_page_object(root_path, project, parents,
                                                         element_name)
            elif elem_type == 'suite':
                if is_dir:
                    errors = file_manager.new_directory_of_type(root_path, project,
                                                                parents, element_name,
                                                                dir_type='suites')
                else:
                    errors = suite_module.new_suite(root_path, project, parents, element_name)
        element = {
            'name': element_name,
            'full_path': dot_path,
            'type': elem_type,
            'is_directory': is_dir
        }
        return json.dumps({'errors': errors, 'project_name': project,
                           'element': element})


@app.route("/new_project/", methods=['POST'])
@login_required
def new_project():
    if request.method == 'POST':
        project_name = request.form['projectName']
        project_name = project_name.strip().replace(' ', '_')
        errors = []
        if len(project_name) < 3:
            errors.append('Project name is too short')
        elif len(project_name) > 50:
            errors.append('Project name is too long')
        elif len(project_name) != len(project_name.strip()):
            errors.append('Leading and trailing spaces are not allowed')
        elif project_name in utils.get_projects(root_path):
            errors.append('A project with that name already exists')
        else:
            utils.create_new_project(root_path, project_name)
        return json.dumps({'errors': errors, 'project_name': project_name})


@app.route("/save_test_case_code/", methods=['POST'])
@login_required
def save_test_case_code():
    if request.method == 'POST':
        project = request.json['project']
        test_case_name = request.json['testCaseName']
        table_test_data = request.json['testData']
        content = request.json['content']
        test_case.save_test_case_code(root_path, project, test_case_name,
                                      content, table_test_data)
        path = test_case.generate_test_case_path(root_path, project, test_case_name)
        _, error = utils.import_module(path)
        return json.dumps({'error': error})


@app.route("/get_global_actions/", methods=['POST'])
@login_required
def get_global_actions():
    if request.method == 'POST':
        global_actions = gui_utils.Golem_action_parser().get_actions()
        return json.dumps(global_actions)


@app.route("/save_page_object/", methods=['POST'])
@login_required
def save_page_object():
    if request.method == 'POST':
        project = request.json['project']
        page_object_name = request.json['pageObjectName']
        elements = request.json['elements']
        functions = request.json['functions']
        import_lines = request.json['importLines']
        page_object.save_page_object(root_path, project, page_object_name,
                                     elements, functions, import_lines)
        return json.dumps('ok')


@app.route("/save_page_object_code/", methods=['POST'])
@login_required
def save_page_object_code():
    if request.method == 'POST':
        project = request.json['project']
        page_object_name = request.json['pageObjectName']
        content = request.json['content']
        path = page_object.generate_page_path(root_path, project, page_object_name)
        page_object.save_page_object_code(root_path, project,
                                          page_object_name, content)
        _, error = utils.import_module(path)
        return json.dumps({'error': error})


@app.route("/run_test_case/", methods=['POST'])
@login_required
def run_test_case():
    if request.method == 'POST':
        project = request.form['project']
        test_name = request.form['testCaseName']
        environment = request.form['environment']
        timestamp = gui_utils.run_test_case(project, test_name, environment)
        return json.dumps(timestamp)


@app.route("/save_test_case/", methods=['POST'])
@login_required
def save_test_case():
    if request.method == 'POST':
        project = request.json['project']
        test_name = request.json['testCaseName']
        description = request.json['description']
        page_objects = request.json['pageObjects']
        test_data_content = request.json['testData']
        test_steps = request.json['testSteps']
        test_case.save_test_case(root_path, project, test_name, description,
                                 page_objects, test_steps, test_data_content)
        return json.dumps('ok')


@app.route("/check_test_case_run_result/", methods=['POST'])
@login_required
def check_test_case_run_result():
    if request.method == 'POST':
        project = request.form['project']
        test_case_name = request.form['testCaseName']
        timestamp = request.form['timestamp']
        path = os.path.join(root_path, 'projects', project, 'reports',
                            'single_tests', test_case_name, timestamp)
        sets = []
        result = {
            'reports': [],
            'logs': [],
            'complete': False
        }
        if os.path.isdir(path):
            for elem in os.listdir(path):
                if os.path.isdir(os.path.join(path, elem)):
                    sets.append(elem)
        # is execution finished?
        result['complete'] = report_parser.is_execution_finished(path, sets)
        for data_set in sets:
            report_path = os.path.join(path, data_set, 'report.json')
            if os.path.exists(report_path):
                test_case_data = report_parser.get_test_case_data(root_path,
                                                                  project,
                                                                  test_case_name,
                                                                  execution=timestamp,
                                                                  test_set=data_set,
                                                                  is_single=True)
                result['reports'].append(test_case_data)
            log_path = os.path.join(path, data_set, 'execution_info.log')
            if os.path.exists(log_path):
                with open(log_path) as log_file:
                    log = log_file.readlines()
                    result['logs'].append(log)
        return json.dumps(result)


@app.route("/run_suite/", methods=['POST'])
@login_required
def run_suite():
    if request.method == 'POST':
        project = request.form['project']
        suite_name = request.form['suite']
        timestamp = gui_utils.run_suite(project, suite_name)
        return json.dumps(timestamp)


@app.route("/save_suite/", methods=['POST'])
@login_required
def save_suite():
    if request.method == 'POST':
        project = request.json['project']
        suite_name = request.json['suite']
        test_cases = request.json['testCases']
        workers = request.json['workers']
        browsers = request.json['browsers']
        environments = request.json['environments']
        suite_module.save_suite(root_path, project, suite_name, test_cases,
                                workers, browsers, environments)
        return json.dumps('ok')


@app.route("/save_settings/", methods=['POST'])
@login_required
def save_settings():
    if request.method == 'POST':
        project = request.json['project']
        project_settings = request.json['projectSettings']
        global_settings = request.json['globalSettings']
        result = {
            'result': 'ok',
            'errors': []
        }
        settings_manager.save_global_settings(root_path, global_settings)
        settings_manager.save_project_settings(root_path, project, project_settings)
        # re-read settings
        test_execution.settings = settings_manager.get_project_settings(root_path, project)
        return json.dumps(result)


@app.route("/save_environments/", methods=['POST'])
@login_required
def save_environments():
    if request.method == 'POST':
        project = request.json['project']
        env_data = request.json['environmentData']
        error = environment_manager.save_environments(root_path, project, env_data)
        return json.dumps(error)


# @app.route("/lock_file/", methods=['POST'])
# @login_required
# def lock_file():
#     if request.method == 'POST':
#         project = request.form['project']
#         user_name = request.form['userName']
#         full_file_name = request.form['fullTestCaseName']
#         lock.lock_file(root_path, project, full_file_name, user_name)
#         return json.dumps('ok')
#
#
# @app.route("/unlock_file/", methods=['POST'])
# @login_required
# def unlock_file():
#     if request.method == 'POST':
#         project = request.form['project']
#         user_name = request.form['userName']
#         full_file_name = request.form['fullTestCaseName']
#         lock.unlock_file(root_path, project, full_file_name, user_name)
#         return json.dumps('ok')


@app.route("/get_supported_browsers/", methods=['POST'])
@login_required
def get_supported_browsers():
    project = request.form['project']
    settings = settings_manager.get_project_settings(root_path, project)
    remote_browsers = settings_manager.get_remote_browser_list(settings)
    default_browsers = gui_utils.get_supported_browsers_suggestions()
    return json.dumps(remote_browsers + default_browsers)


@app.route("/get_environments/", methods=['POST'])
@login_required
def get_environments():
    project = request.form['project']
    return json.dumps(environment_manager.get_envs(root_path, project))


@app.route("/report/get_last_executions/", methods=['POST'])
@login_required
def get_last_executions():
    if request.method == 'POST':
        projects = request.json['projects']
        suite = request.json['suite']
        limit = request.json['limit']
        project_data = report_parser.get_last_executions(root_path, projects, suite, limit)
        return jsonify(projects=project_data)


@app.route("/report/get_execution_data/", methods=['POST'])
@login_required
def get_execution_data():
    if request.method == 'POST':
        project = request.form['project']
        suite = request.form['suite']
        execution = request.form['execution']
        execution_data = report_parser.get_execution_data(workspace=root_path, project=project,
                                                          suite=suite, execution=execution)
        response = jsonify(execution_data)
        return response


@app.route("/report/get_project_health_data/", methods=['POST'])
@login_required
def get_project_health_data():
    if request.method == 'POST':
        project = request.form['project']
        project_data = report_parser.get_last_executions(root_path, projects=[project],
                                                         suite=None, limit=1)
        health_data = {}
        for suite, executions in project_data[project].items():
            execution_data = report_parser.get_execution_data(workspace=root_path,
                                                              project=project,
                                                              suite=suite,
                                                              execution=executions[0])
            health_data[suite] = {
                'execution': executions[0],
                'total': execution_data['total_tests'],
                'totals_by_result': execution_data['totals_by_result']
            }
        return jsonify(health_data)


@app.route("/page/page_exists/", methods=['POST'])
@login_required
def page_exists():
    if request.method == 'POST':
        project = request.form['project']
        full_page_name = request.form['fullPageName']
        page_exists = page_object.page_exists(root_path, project, full_page_name)
        return jsonify(page_exists)


############
# END OF API
############


#########
# GENERAL
#########

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@login_manager.user_loader
def load_user(user_id):
    return user.get_user_from_id(user_id)


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login?next=' + request.path)


@app.before_request
def before_request():
    g.user = current_user


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', message=error.description), 404


################
# END OF GENERAL
################


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
