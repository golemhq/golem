import json
import os

from flask import Flask, render_template, request, redirect, jsonify, g
from flask.ext.login import (
                        LoginManager,
                        login_user,
                        logout_user,
                        current_user,
                        login_required)

from golem.core import utils
from . import gui_utils, test_case, page_object, data, user


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
                    if not user.password_is_correct(
                                    username, password, root_path):
                        result['errors'].append(
                                          'Username and password do not match')
        if not next_url:
            next_url = '/'

        if len(result['errors']) > 0:
            return render_template(
                'login.html',
                next_url=next_url,
                errors=result['errors'])
        else:
            new_user = user.User()
            new_user.username = username
            new_user.id = user_id
            # check if user is already logged in
            if g.user is not None and g.user.is_authenticated:
                return redirect(next_url)
            else:
                login_user(new_user)
                return redirect(next_url)
    else:
        next_url = request.args.get('next')
        return render_template(
            'login.html',
            next_url=next_url,
            errors=[])


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
    if not user.has_permissions_to_project(g.user.id, project, root_path):
        return render_template('not_permission.html')

    test_cases = utils.get_test_cases(
                    root_path,
                    project)

    page_objects = utils.get_page_objects(
                            root_path,
                            project)

    return render_template(
                           'project.html',
                           test_cases=test_cases,
                           project=project,
                           page_objects=page_objects)


# TEST CASE VIEW
@app.route("/p/<project>/tc/<test_case_name>/")
@login_required
def test_case_view(project, test_case_name):
    # check if user has permissions for this project
    if not user.has_permissions_to_project(g.user.id, project, root_path):
        return render_template('not_permission.html')

    tc_name, parents = utils.separate_file_from_parents(test_case_name)

    test_case_data = test_case.parse_test_case(
                                        root_path,
                                        project,
                                        parents,
                                        tc_name)

    test_data = utils.get_test_data(root_path,
                                   project,
                                   test_case_name)
    print test_data
    return render_template(
                    'test_case.html',
                    project=project,
                    test_case_data=test_case_data,
                    test_case_name=tc_name,
                    full_test_case_name=test_case_name,
                    test_data=test_data)


@app.route("/get_page_objects/", methods=['POST'])
def get_page_objects():

    if request.method == 'POST':
        projectname = request.form['project']

        page_objects = utils.get_page_objects_as_list(
                            root_path,
                            projectname)

        return json.dumps(page_objects)


@app.route("/get_selected_page_object_elements/", methods=['POST'])
def get_selected_page_object_elements():

    if request.method == 'POST':
        projectname = request.form['project']
        page_object_name = request.form['pageObject']

        po_elements = page_object.get_page_object_elements(root_path,
                                                           projectname,
                                                           page_object_name)

        return json.dumps(po_elements)


@app.route("/get_datos_values/", methods=['POST'])
def get_datos_values():

    if request.method == 'POST':
        projectname = request.form['project']
        canal = request.form['canal']
        test_case_name = request.form['testCaseName']

        datos_values = worksheet.get_datos_values(
                            global_settings['workspace'],
                            projectname,
                            canal,
                            test_case_name,
                            global_settings['planilla_datos'])

        return json.dumps(datos_values)


@app.route("/nuevo_test_case/", methods=['POST'])
def nuevo_test_case():

    if request.method == 'POST':
        projectname = request.form['project']
        parents = request.form['parents'].split('.')
        tc_name = request.form['testCaseName']

        errors = []

        # check if a file already exists
        if gui_utils.file_already_exists(
                        root_path,
                        projectname,
                        'test_cases',
                        parents,
                        tc_name):
            errors.append('A file with that name already exists')

        if not errors:
            test_case.new_test_case(
                            root_path,
                            projectname,
                            parents,
                            tc_name)

        return json.dumps({
            'errors': errors,
            'project_name': projectname,
            'tc_name': tc_name})


@app.route("/new_directory_test_case/", methods=['POST'])
def new_directory_test_case():

    if request.method == 'POST':
        projectname = request.form['project']
        parents = request.form['parents'].split('.')
        directory_name = request.form['directoryName'].replace('/', '')

        errors = []

        # check if a directory already exists
        if gui_utils.directory_already_exists(
                        root_path,
                        projectname,
                        'test_cases',
                        parents,
                        directory_name):
            errors.append('A directory with that name already exists')

        if not errors:
            gui_utils.new_directory(
                    root_path,
                    projectname,
                    parents,
                    directory_name)

        return json.dumps({
            'errors': errors,
            'project_name': projectname,
            'directory_name': directory_name})


@app.route("/new_page_object/", methods=['POST'])
def new_page_object():

    if request.method == 'POST':
        projectname = request.form['project']
        parents = request.form['parents'].split('.')
        page_object_name = request.form['pageObjectName']

        errors = []

        # check if a file already exists
        if gui_utils.file_already_exists(
                        root_path,
                        projectname,
                        'pages',
                        parents,
                        page_object_name):
            errors.append('A file with that name already exists')

        if not errors:
            page_object.new_page_object(
                            root_path,
                            projectname,
                            parents,
                            page_object_name)

        return json.dumps({
            'errors': errors,
            'project_name': projectname,
            'page_object_name': page_object_name})


@app.route("/new_directory_page_object/", methods=['POST'])
def new_directory_page_object():

    if request.method == 'POST':
        projectname = request.form['project']
        parents = request.form['parents'].split('.')
        directory_name = request.form['directoryName'].replace('/', '')

        errors = []

        # check if a directory already exists
        if gui_utils.directory_already_exists(
                        root_path,
                        projectname,
                        'pages',
                        parents,
                        directory_name):
            errors.append('A directory with that name already exists')

        if not errors:
            gui_utils.new_directory_page_object(
                    root_path,
                    projectname,
                    parents,
                    directory_name)

        return json.dumps({
            'errors': errors,
            'project_name': projectname,
            'directory_name': directory_name})


@app.route("/get_global_actions/", methods=['POST'])
def get_global_actions():

    if request.method == 'POST':
        global_actions = gui_utils.get_global_actions()
        return json.dumps(global_actions)


@app.route("/p/<project>/page/<full_page_name>/")
@login_required
def page_view(project, full_page_name):
    if not user.has_permissions_to_project(g.user.id, project, root_path):
        return render_template('not_permission.html')

    page_object_data = page_object.get_page_object_elements(root_path,
                                                            project,
                                                            full_page_name)

    return render_template(
                    'page_object.html',
                    project=project,
                    page_object_data=page_object_data,
                    page_name=full_page_name)


@app.route("/save_page_object/", methods=['POST'])
def save_page_object():

    if request.method == 'POST':
        projectname = request.json['project']
        page_object_name = request.json['pageObjectName']
        elements = request.json['elements']

        page_object.save_page_object(
            root_path,
            projectname,
            page_object_name,
            elements)

        return json.dumps('ok')


@app.route("/save_test_case/", methods=['POST'])
def save_test_case():

    if request.method == 'POST':
        projectname = request.json['project']
        test_case_name = request.json['testCaseName']
        description = request.json['description']
        page_objects = request.json['pageObjects']
        test_data = request.json['testData']
        test_steps = request.json['testSteps']

        data.save_test_data(
            root_path,
            projectname,
            test_case_name,
            test_data)

        test_case.save_test_case(
            root_path,
            projectname,
            test_case_name,
            description,
            page_objects,
            test_steps)

        return json.dumps('ok')


@app.route("/run_test_case/", methods=['POST'])
def run_test_case():

    if request.method == 'POST':
        projectname = request.form['project']
        test_case_name = request.form['testCaseName']

        gui_utils.run_test_case(projectname, test_case_name)

        return json.dumps('ok')


@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect('/')


@login_manager.user_loader
def load_user(user_id):
    return user.get_user(user_id, root_path)


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login?next=' + request.path)


@app.before_request
def before_request():
    g.user = current_user


if __name__ == "__main__":

    global_settings = gui_utils.read_global_settings()

    app.run(host='0.0.0.0', debug=True)
