import json
import os

from flask import (Flask,
                   jsonify,
                   render_template,
                   request,
                   redirect,
                   g,
                   send_from_directory,
                   abort)

from flask_login import (LoginManager,
                         login_user,
                         logout_user,
                         current_user,
                         login_required)

from golem.core import (utils,
                        settings_manager,
                        test_case,
                        page_object,
                        suite,
                        data,
                        test_execution,
                        changelog,
                        lock)

from . import gui_utils, user, report_parser


app = Flask(__name__)

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

login_manager = LoginManager()
login_manager.init_app(app)

root_path = None

# LOGIN VIEW
@app.route('/login/', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        result = {
            'errors': []
        }
        username = request.form['username']
        password = request.form['password']
        next_url = request.form['next']

        if not username:
            result['errors'].append('Username is required')
        else:
            user_id = user.user_exists(username, root_path)
            if not user_id:
                result['errors'].append('Username does not exists')
            else:
                if not password:
                    result['errors'].append('Password is required')
                else:
                    if not user.password_is_correct(username, password, root_path):
                        result['errors'].append('Username and password do not match')
        if not next_url:
            next_url = '/'

        if len(result['errors']) > 0:
            return render_template('login.html', next_url=next_url, errors=result['errors'])
        else:
            new_user = user.User()
            new_user.username = username
            new_user.id = user_id
            new_user.is_admin = user.is_admin(user_id, root_path)
            # check if user is already logged in
            if g.user is not None and g.user.is_authenticated:
                return redirect(next_url)
            else:
                login_user(new_user)
                return redirect(next_url)
    else:
        next_url = request.args.get('next')
        return render_template('login.html', next_url=next_url, errors=[])


# INDEX
@app.route("/")
@login_required
def index():
    projects = utils.get_projects(root_path)
    return render_template('index.html', projects=projects)


# PROJECT VIEW
@app.route("/p/<project>/")
@login_required
def project(project):
    if not user.has_permissions_to_project(g.user.id, project, root_path, 'gui'):
        return render_template('not_permission.html')
    elif not utils.project_exists(root_path, project):
        abort(404, 'This page does not exists.')
    else:
        return render_template('project_dashboard.html', project=project)


@app.route("/project/get_tests/", methods=['POST'])
def get_tests():
    if request.method == 'POST':
        project = request.form['project']
        tests = utils.get_test_cases(root_path, project)
        return json.dumps(tests)


@app.route("/project/get_pages/", methods=['POST'])
def get_pages():
    if request.method == 'POST':
        project = request.form['project']
        pages = utils.get_pages(root_path, project)
        return json.dumps(pages)


@app.route("/project/get_suites/", methods=['POST'])
def get_suite():
    if request.method == 'POST':
        project = request.form['project']
        suites = utils.get_suites(root_path, project)
        return json.dumps(suites)


@app.route("/delete_element/", methods=['POST'])
def delete_element():
    if request.method == 'POST':
        project = request.form['project']
        elem_type = request.form['elemType']
        full_path = request.form['fullPath']
        errors = utils.delete_element(root_path, project, elem_type, full_path)
        return json.dumps(errors)

@app.route("/duplicate_element/", methods=['POST'])
def duplicate_element():
    if request.method == 'POST':
        project = request.form['project']
        elem_type = request.form['elemType']
        full_path = request.form['fullPath']
        new_file_full_path = request.form['newFileFullPath']
        errors = utils.duplicate_element(root_path, project, elem_type,
                                         full_path, new_file_full_path)
        return json.dumps(errors)


# TEST CASE VIEW
@app.route("/p/<project>/test/<test_case_name>/")
@login_required
def test_case_view(project, test_case_name):
    # check if user has permissions for this project
    if not user.has_permissions_to_project(g.user.id, project, root_path, 'gui'):
        return render_template('not_permission.html')

    # check if the file is locked
    # is_locked_by = lock.is_file_locked(root_path, project, test_case_name)
    # print(is_locked_by, g.user.username)
    # if is_locked_by and is_locked_by != g.user.username:
    #     abort(404, 'This file is locked by someone else.')
    # else:
    tc_name, parents = utils.separate_file_from_parents(test_case_name)
    test_case_contents = test_case.get_test_case_content(project, test_case_name)
    test_data = utils.get_test_data_dict_list(root_path, project, test_case_name)

    return render_template('test_case.html', project=project,
                           test_case_contents=test_case_contents, test_case_name=tc_name,
                           full_test_case_name=test_case_name, test_data=test_data)


@app.route("/p/<project>/test/<test_case_name>/code/")
@login_required
def test_case_code_view(project, test_case_name):
    # check if user has permissions for this project
    if not user.has_permissions_to_project(g.user.id, project, root_path, 'gui'):
        return render_template('not_permission.html')

    tc_name, parents = utils.separate_file_from_parents(test_case_name)
    test_case_contents = test_case.get_test_case_content(project, test_case_name)
    test_data = utils.get_test_data_dict_list(root_path, project, test_case_name)

    return render_template('test_case_code.html', project=project, 
                           test_case_contents=test_case_contents, test_case_name=tc_name,
                           full_test_case_name=test_case_name, test_data=test_data)


@app.route("/get_page_objects/", methods=['POST'])
def get_page_objects():
    if request.method == 'POST':
        project = request.form['project']
        path = os.path.join(root_path, 'projects', project, 'pages')
        page_objects = utils.get_files_in_directory_dotted_path(path)
        return json.dumps(page_objects)


@app.route("/get_selected_page_object_elements/", methods=['POST'])
def get_selected_page_object_elements():
    if request.method == 'POST':
        project = request.form['project']
        page_name = request.form['pageObject']
        po_elements = page_object.get_page_object_content(root_path, project, page_name)
        return json.dumps(po_elements)


@app.route("/new_tree_element/", methods=['POST'])
def new_tree_element():

    if request.method == 'POST':
        project = request.form['project']
        elem_type = request.form['elementType']
        is_dir = json.loads(request.form['isDir'])
        full_path = request.form['fullPath'].split('.')
        element_name = full_path[-1]
        parents = full_path[:-1]
        errors = []

        if is_dir:
            element_name = element_name.replace('/', '')
        for c in element_name:
            if not c.isalnum() and not c in ['-', '_']:
                errors.append('Only letters, numbers, \'-\' and \'_\' are allowed')
                break
        if not errors:
            if elem_type == 'test_dir':
                errors = gui_utils.new_directory_test_case(root_path, project, parents, element_name)
            elif elem_type == 'page_dir':
                errors = gui_utils.new_directory_page_object(root_path, project, parents, element_name)
            elif elem_type == 'test':
                errors = test_case.new_test_case(root_path, project, parents, element_name)
                changelog.log_change(root_path, project, 'CREATE', 'test',
                                     full_path, g.user.username)
            elif elem_type == 'page':
                errors = page_object.new_page_object(root_path, project, parents, element_name)
            elif elem_type == 'suite':
                errors = suite.new_suite(root_path, project, element_name)
        element = {
            'name': element_name,
            'full_path': '.'.join(full_path),
            'type': elem_type,
            'is_directory': is_dir
        }
        return json.dumps({'errors': errors, 'project_name': project,
                           'element': element})


@app.route("/new_project/", methods=['POST'])
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


@app.route("/get_global_actions/", methods=['POST'])
def get_global_actions():

    if request.method == 'POST':
        global_actions = gui_utils.get_global_actions()
        return json.dumps(global_actions)


@app.route("/p/<project>/page/<full_page_name>/")
@login_required
def page_view(project, full_page_name):
    if not user.has_permissions_to_project(g.user.id, project, root_path, 'gui'):
        return render_template('not_permission.html')

    page_object_data = page_object.get_page_object_content(root_path, project, full_page_name)

    return render_template('page_object.html', project=project, page_object_data=page_object_data,
                           page_name=full_page_name)


@app.route("/p/<project>/page/<full_page_name>/code/")
@login_required
def page_code_view(project, full_page_name):
    if not user.has_permissions_to_project(g.user.id, project, root_path, 'gui'):
        return render_template('not_permission.html')
    page_object_data = page_object.get_page_object_content(root_path, project, full_page_name)
    return render_template('page_object_code.html', project=project,
                           page_object_data=page_object_data, page_name=full_page_name)


@app.route("/save_page_object/", methods=['POST'])
def save_page_object():

    if request.method == 'POST':
        projectname = request.json['project']
        page_object_name = request.json['pageObjectName']
        elements = request.json['elements']
        functions = request.json['functions']
        import_lines = request.json['importLines']
        page_object.save_page_object(root_path, projectname, page_object_name,
                                     elements, functions, import_lines)
        return json.dumps('ok')


@app.route("/save_page_object_code/", methods=['POST'])
def save_page_object_code():
    if request.method == 'POST':
        projectname = request.json['project']
        page_object_name = request.json['pageObjectName']
        content = request.json['content']
        error = utils.code_syntax_is_valid(content)
        page_object.save_page_object_code(root_path, projectname,
                                          page_object_name, content)
        return json.dumps(error)


@app.route("/save_test_case/", methods=['POST'])
def save_test_case():

    if request.method == 'POST':
        project = request.json['project']
        test_name = request.json['testCaseName']
        description = request.json['description']
        page_objects = request.json['pageObjects']
        test_data = request.json['testData']
        test_steps = request.json['testSteps']

        data.save_test_data(root_path, project, test_name, test_data)

        test_case.save_test_case(root_path, project, test_name, description,
                                 page_objects, test_steps)

        changelog.log_change(root_path, project, 'MODIFY', 'test', test_name,
                              g.user.username)
        return json.dumps('ok')


@app.route("/save_test_case_code/", methods=['POST'])
def save_test_case_code():

    if request.method == 'POST':
        projectname = request.json['project']
        test_case_name = request.json['testCaseName']
        test_data = request.json['testData']
        content = request.json['content']

        print(test_data)

        data.save_test_data(root_path, projectname, test_case_name, test_data)
        test_case.save_test_case_code(root_path, projectname, test_case_name, content)

        return json.dumps('ok')


@app.route("/run_test_case/", methods=['POST'])
def run_test_case():
    if request.method == 'POST':
        project = request.form['project']
        test_name = request.form['testCaseName']

        timestamp = gui_utils.run_test_case(project, test_name)

        changelog.log_change(root_path, project, 'RUN', 'test', test_name, g.user.username)
        return json.dumps(timestamp)


@app.route("/check_test_case_run_result/", methods=['POST'])
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
                sets.append(elem)  

        # is execution finished?
        result['complete'] = report_parser.is_execution_finished(path, sets)

        for data_set in sets:
            report_path = os.path.join(path, data_set, 'report.json')
            if os.path.exists(report_path):
                test_case_data = report_parser.get_test_case_data(root_path, project,
                                                              test_case_name, execution=timestamp,
                                                              test_set=data_set, is_single=True)
                result['reports'].append(test_case_data)

            log_path = os.path.join(path, data_set, 'execution_console.log')
            if os.path.exists(log_path):
                with open(log_path) as log_file:
                    log = log_file.readlines()
                    result['logs'].append(log)

        return json.dumps(result)


@app.route("/change_test_name/", methods=['POST'])
def change_test_name():
    if request.method == 'POST':
        project = request.form['project']
        test_name = request.form['testName']
        new_test_name = request.form['newTestName']

        test, parents = utils.separate_file_from_parents(test_name)
        current_path = os.path.join(root_path, 'projects', project, 'tests',
                                    os.sep.join(parents), '{}.py'.format(test))

        test, parents = utils.separate_file_from_parents(new_test_name)
        new_path = os.path.join(root_path, 'projects', project, 'tests',
                                os.sep.join(parents), '{}.py'.format(test))

        try:
            os.rename(current_path, new_path)
            return json.dumps('ok')
        except:
            return json.dumps('error')


@app.route("/run_suite/", methods=['POST'])
def run_suite():
    if request.method == 'POST':
        projectname = request.form['project']
        suite_name = request.form['suite']

        timestamp = gui_utils.run_suite(projectname, suite_name)

        return json.dumps(timestamp)


@app.route("/p/<project>/suite/<suite>/")
def suite_view(project, suite):
    if not user.has_permissions_to_project(g.user.id, project, root_path, 'gui'):
        return render_template('not_permission.html')

    all_test_cases = utils.get_test_cases(root_path, project)
    selected_tests = utils.get_suite_test_cases(root_path, project, suite)
    worker_amount = utils.get_suite_amount_of_workers(root_path, project, suite)
    browsers = utils.get_suite_browsers(root_path, project, suite)
    browsers = ', '.join(browsers)
    default_browser = test_execution.settings['default_driver']

    return render_template('suite.html', project=project, all_test_cases=all_test_cases['sub_elements'],
                           selected_tests=selected_tests, suite=suite, worker_amount=worker_amount,
                           browsers=browsers, default_browser=default_browser)


@app.route("/save_suite/", methods=['POST'])
def save_suite():

    if request.method == 'POST':
        project = request.json['project']
        suite_name = request.json['suite']
        test_cases = request.json['testCases']
        workers = request.json['workers']
        browsers = request.json['browsers']

        suite.save_suite(root_path, project, suite_name, test_cases, workers, browsers)

        return json.dumps('ok')


@app.route("/p/<project>/settings/")
def settings_view(project):
    if not user.has_permissions_to_project(g.user.id, project, root_path, 'gui'):
        return render_template('not_permission.html')
    global_settings = settings_manager.get_global_settings_as_string()
    project_settings = settings_manager.get_project_settings_as_string(project)
    return render_template('settings.html', project=project,
                           global_settings=global_settings, settings=project_settings)


@app.route("/save_settings/", methods=['POST'])
def save_settings():
    if request.method == 'POST':
        projectname = request.json['project']
        project_settings = request.json['projectSettings']
        global_settings = request.json['globalSettings']
        result = {
            'result': 'ok',
            'errors': []
        }
        settings_manager.save_settings(root_path, projectname,
                                       project_settings, global_settings)
        return json.dumps(result)


@app.route("/lock_file/", methods=['POST'])
def lock_file():
    if request.method == 'POST':
        project = request.form['project']
        user_name = request.form['userName']
        full_file_name = request.form['fullTestCaseName']
        lock.lock_file(root_path, project, full_file_name, user_name)
        return json.dumps('ok')


@app.route("/unlock_file/", methods=['POST'])
def unlock_file():
    if request.method == 'POST':
        project = request.form['project']
        user_name = request.form['userName']
        full_file_name = request.form['fullTestCaseName']
        lock.unlock_file(root_path, project, full_file_name, user_name)
        return json.dumps('ok')


@app.route("/get_supported_browsers/", methods=['POST'])
def get_supported_browsers():
    return json.dumps(gui_utils.get_supported_browsers_suggestions())



@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect('/')


########
# REPORT
########

# REPORT INDEX
@app.route("/report/")
@login_required
def report_dashboard():
    if not user.has_permissions_to_project(g.user.id, project, root_path, 'report'):
        return render_template('not_permission.html')
    else:
        return render_template('report/report_dashboard.html', project='', suite='')


# REPORT INDEX
@app.route("/report2/")
@login_required
def report_index2():
    if not user.has_permissions_to_project(g.user.id, project, root_path, 'report'):
        return render_template('not_permission.html')
    else:
        return render_template('report/report_dashboard2.html', project='', suite='')



@app.route("/report/project/<project>/")
@login_required
def report_dashboard_project(project):
    if not user.has_permissions_to_project(g.user.id, project, root_path, 'report'):
        return render_template('not_permission.html')
    else:
        return render_template('report/report_dashboard.html', project=project, suite='')


@app.route("/report/project/<project>/suite/<suite>/")
@login_required
def report_dashboard_suite(project, suite):
    if not user.has_permissions_to_project(g.user.id, project, root_path, 'report'):
        return render_template('not_permission.html')
    else:
        return render_template('report/report_dashboard.html', project=project, suite=suite)


@app.route("/report/project/<project>/<suite>/<execution>/")
@login_required
def report_execution(project, suite, execution):
    if not user.has_permissions_to_project(g.user.id, project, root_path, 'report'):
        return render_template('not_permission.html')
    else:
        formatted_date = report_parser.get_start_date_time_from_timestamp(execution)
        return render_template('report/report_execution.html', project=project, suite=suite,
                               execution=execution, formatted_date=formatted_date)


@app.route("/report2/project/<project>/<suite>/<execution>/")
@login_required
def execution_report2(project, suite, execution):
    if not user.has_permissions_to_project(g.user.id, project, root_path, 'report'):
        return render_template('not_permission.html')
    else:
        formatted_date = report_parser.get_start_date_time_from_timestamp(execution)
        return render_template('report/execution_report2.html', project=project, suite=suite,
                               execution=execution, formatted_date=formatted_date)


@app.route("/report/project/<project>/<suite>/<execution>/<test_case>/<test_set>/")
@login_required
def report_test(project, suite, execution, test_case, test_set):
    if not user.has_permissions_to_project(g.user.id, project, root_path, 'report'):
        return render_template('not_permission.html')
    test_case_data = report_parser.get_test_case_data(root_path, project, test_case,
                                                      suite=suite, execution=execution,
                                                      test_set=test_set)
    return render_template('report/report_test.html', project=project, suite=suite,
                           execution=execution, test_case=test_case, test_set=test_set,
                           test_case_data=test_case_data)

@app.route("/report2/project/<project>/<suite>/<execution>/<test_case>/<test_set>/")
@login_required
def report_test2(project, suite, execution, test_case, test_set):
    if not user.has_permissions_to_project(g.user.id, project, root_path, 'report'):
        return render_template('not_permission.html')
    test_case_data = report_parser.get_test_case_data(root_path, project, test_case,
                                                      suite=suite, execution=execution,
                                                      test_set=test_set)
    return render_template('report/report_test2.html', project=project, suite=suite,
                           execution=execution, test_case=test_case, test_set=test_set,
                           test_case_data=test_case_data)


@app.route("/report/get_last_executions/", methods=['POST'])
def get_last_executions():
    if request.method == 'POST':
        project = request.form['project']
        suite = request.form['suite']
        limit = request.form['limit']
        #if suite:

        project_data = report_parser.get_last_executions(root_path, project, suite, limit)
        return jsonify(projects=project_data)


@app.route("/report/get_execution_data/", methods=['POST'])
def get_execution_data():
    if request.method == 'POST':

        project = request.form['project']
        suite = request.form['suite']
        execution = request.form['execution']
        execution_data = report_parser.get_execution_data(root_path, project, suite, execution)
        return jsonify(execution_data)


@app.route("/report/get_project_health_data/", methods=['POST'])
def get_project_health_data():
    if request.method == 'POST':
        project = request.form['project']
        project_data = report_parser.get_last_executions(root_path, project=project, suite=None, limit=1)
        
        health_data = {}

        for suite, executions in project_data[project].items():
            execution_data = report_parser.get_execution_data(root_path,
                                                              project,
                                                              suite,
                                                              executions[0])
            print(execution_data['total_cases_ok'], execution_data['total_cases'])
            health_data[suite] = {
                'execution': executions[0],
                'total': execution_data['total_cases'],
                'total_ok': execution_data['total_cases_ok'],
                'total_fail': execution_data['total_cases_fail']
            }

        return jsonify(health_data)



@app.route('/report/screenshot/<project>/<suite>/<execution>/<test_case>/<test_set>/<scr>/')
def screenshot_file(project, suite, execution, test_case, test_set, scr):
    screenshot_path = os.path.join(root_path, 'projects', project, 'reports',
                                   suite, execution, test_case, test_set)
    return send_from_directory(screenshot_path, '{}.png'.format(scr))


@app.route('/test/screenshot/<project>/<test>/<execution>/<test_set>/<scr>/')
def screenshot_file2(project, test, execution, test_set, scr):
    screenshot_path = os.path.join(root_path, 'projects', project, 'reports',
                                   'single_tests', test, execution, test_set)
    return send_from_directory(screenshot_path, '{}.png'.format(scr))


###############
# END OF REPORT
###############


@login_manager.user_loader
def load_user(user_id):
    return user.get_user(user_id, root_path)


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login?next=' + request.path)


@app.before_request
def before_request():
    g.user = current_user


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', message=error.description), 404


if __name__ == "__main__":

    app.run(host='0.0.0.0', debug=True)
