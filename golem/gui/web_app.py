"""Golem GUI main web app blueprint"""
import os

from flask import abort, redirect, render_template, request, url_for
from flask.blueprints import Blueprint
from flask_login import current_user, login_user, login_required, logout_user

from golem.core import (environment_manager, settings_manager, session,
                        utils, test_directory)
from golem.core.page import Page
from golem.core.test import Test
from golem.core import test_data as test_data_module
from golem.core import suite as suite_module
from golem.core.project import Project

from golem.gui.user_management import Users, Permissions
from golem.gui.gui_utils import project_exists, permission_required, is_safe_url


webapp_bp = Blueprint('webapp', __name__)


# LOGIN VIEW
@webapp_bp.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('webapp.index'))
    if request.method == 'POST':
        errors = []
        username = request.form['username']
        password = request.form['password']
        next_url = request.form['next']
        if not username:
            errors.append('Username is required')
        elif not password:
            errors.append('Password is required')
        elif not Users.user_exists(username):
            errors.append('Username does not exists')
        elif not Users.verify_password(username, password):
            errors.append('Username and password do not match')

        if errors:
            return render_template('login.html', next_url=next_url, errors=errors)
        else:
            login_user(Users.get_user_by_username(username))
            if not next_url or not is_safe_url(next_url):
                next_url = '/'
            return redirect(next_url)
    else:
        next_url = request.args.get('next')
        if not next_url or not is_safe_url(next_url):
            next_url = '/'
        return render_template('login.html', next_url=next_url, errors=[])


# INDEX VIEW
@webapp_bp.route("/")
@login_required
def index():
    """If user is admin or has '*' in report permissions they will
    have access to every project. Otherwise limit the project
    list to gui_permissions
    """
    projects = test_directory.get_projects()
    if not current_user.is_superuser:
        user_projects = current_user.project_list
        projects = [p for p in user_projects if p in projects]
    return render_template('index.html', projects=projects)


# PROJECT VIEW - redirect to to /project/suites/
@webapp_bp.route("/project/<project>/")
@login_required
@project_exists
@permission_required(Permissions.REPORTS_ONLY)
def project_view(project):
    user_weight = current_user.project_weight(project)
    if user_weight == Permissions.weights[Permissions.REPORTS_ONLY]:
        return redirect('/report/project/{}/'.format(project))
    else:
        return redirect('/project/{}/suites/'.format(project))


# PROJECT TESTS VIEW
@webapp_bp.route('/project/<project>/tests/', defaults={'path': ''})
@webapp_bp.route("/project/<project>/tests/<path:path>/")
@login_required
@project_exists
@permission_required(Permissions.READ_ONLY)
def project_tests(project, path):
    return render_template('list/test_list.html', project=project)


# PROJECT SUITES VIEW
@webapp_bp.route('/project/<project>/suites/', defaults={'path': ''})
@webapp_bp.route("/project/<project>/suites/<path:path>/")
@login_required
@project_exists
@permission_required(Permissions.READ_ONLY)
def project_suites(project, path):
    return render_template('list/suite_list.html', project=project)


# PROJECT PAGES VIEW
@webapp_bp.route('/project/<project>/pages/', defaults={'path': ''})
@webapp_bp.route("/project/<project>/pages/<path:path>/")
@login_required
@project_exists
@permission_required(Permissions.READ_ONLY)
def project_pages(project, path):
    return render_template('list/page_list.html', project=project)


# TEST CASE VIEW
@webapp_bp.route("/project/<project>/test/<test_name>/")
@login_required
@project_exists
@permission_required(Permissions.READ_ONLY)
def test_case_view(project, test_name):
    test = Test(project, test_name)
    if not test.exists:
        abort(404, 'The test {} does not exist'.format(test_name))
    _, error = utils.import_module(test.path)
    if error:
        url = url_for('webapp.test_case_code_view', project=project, test_name=test_name)
        content = ('<h4>There are errors in the test</h4>'
                   '<p>There are errors and the test cannot be displayed, '
                   'open the test code editor to solve them.</p>'
                   '<a class="btn btn-default" href="{}">Open Test Code</a>'
                   .format(url))
        return render_template('common_element_error.html', project=project,
                               item_name=test_name, content=content)
    else:
        test_data = test_data_module.get_test_data(project, test_name,
                                                   repr_strings=True)
        return render_template('test_builder/test_case.html', project=project,
                               test_components=test.components,
                               test_case_name=test.stem_name,
                               full_test_case_name=test_name,
                               test_data=test_data)


# TEST CASE CODE VIEW
@webapp_bp.route("/project/<project>/test/<test_name>/code/")
@login_required
@project_exists
@permission_required(Permissions.READ_ONLY)
def test_case_code_view(project, test_name):
    test = Test(project, test_name)
    if not test.exists:
        abort(404, 'The test {} does not exist'.format(test_name))
    _, error = utils.import_module(test.path)
    external_data = test_data_module.get_external_test_data(project, test_name)
    test_data_setting = session.settings['test_data']
    return render_template('test_builder/test_case_code.html', project=project,
                           test_case_contents=test.code, test_case_name=test.stem_name,
                           full_test_case_name=test_name, test_data=external_data,
                           test_data_setting=test_data_setting, error=error)


# PAGE OBJECT VIEW
@webapp_bp.route("/project/<project>/page/<page_name>/")
@login_required
@project_exists
@permission_required(Permissions.READ_ONLY)
def page_view(project, page_name, no_sidebar=False):
    page = Page(project, page_name)
    if not page.exists:
        abort(404, 'The page {} does not exist'.format(page_name))
    _, error = utils.import_module(page.path)
    if error:
        if no_sidebar:
            url = url_for('webapp.page_code_view_no_sidebar', project=project,
                          page_name=page_name)
        else:
            url = url_for('webapp.page_code_view', project=project, page_name=page_name)
        content = ('<h4>There are errors in the page</h4>'
                   '<p>There are errors and the page cannot be displayed, '
                   'open the page code editor to solve them.</p>'
                   '<a class="btn btn-default" href="{}">Open Page Code</a>'
                   .format(url))
        return render_template('common_element_error.html', project=project,
                               item_name=page_name, content=content,
                               no_sidebar=no_sidebar)
    else:
        return render_template('page_builder/page_object.html',
                               project=project,
                               page_object_data=page.components,
                               page_name=page_name,
                               no_sidebar=no_sidebar)


# PAGE OBJECT VIEW no sidebar
@webapp_bp.route("/project/<project>/page/<page_name>/no_sidebar/")
@login_required
@permission_required(Permissions.READ_ONLY)
def page_view_no_sidebar(project, page_name):
    return page_view(project=project, page_name=page_name, no_sidebar=True)


# PAGE OBJECT CODE VIEW
@webapp_bp.route("/project/<project>/page/<page_name>/code/")
@login_required
@project_exists
@permission_required(Permissions.READ_ONLY)
def page_code_view(project, page_name, no_sidebar=False):
    page = Page(project, page_name)
    if not page.exists:
        abort(404, 'The page {} does not exist'.format(page_name))
    _, error = utils.import_module(page.path)
    return render_template('page_builder/page_object_code.html', project=project,
                           page_object_code=page.code, page_name=page_name,
                           error=error, no_sidebar=no_sidebar)


# PAGE OBJECT CODE VIEW no sidebar
@webapp_bp.route("/project/<project>/page/<page_name>/no_sidebar/code/")
@login_required
@permission_required(Permissions.READ_ONLY)
def page_code_view_no_sidebar(project, page_name):
    return page_code_view(project=project, page_name=page_name, no_sidebar=True)


# SUITE VIEW
@webapp_bp.route("/project/<project>/suite/<suite>/")
@login_required
@project_exists
@permission_required(Permissions.READ_ONLY)
def suite_view(project, suite):
    suite_obj = suite_module.Suite(project, suite)
    if not suite_obj.exists:
        abort(404, 'The suite {} does not exist'.format(suite))
    all_tests = Project(project).test_tree
    default_browser = session.settings['default_browser']
    return render_template('suite.html', project=project,
                           all_test_cases=all_tests['sub_elements'],
                           selected_tests=suite_obj.tests, suite=suite,
                           processes=suite_obj.processes, browsers=suite_obj.browsers,
                           default_browser=default_browser,
                           environments=suite_obj.environments, tags=suite_obj.tags)


# GLOBAL SETTINGS VIEW
@webapp_bp.route("/settings/")
@login_required
@permission_required(Permissions.SUPER_USER)
def global_settings():
    settings = settings_manager.get_global_settings_as_string()
    return render_template('settings/global_settings.html', settings=settings)


# PROJECT SETTINGS VIEW
@webapp_bp.route("/project/<project>/settings/")
@login_required
@project_exists
@permission_required(Permissions.READ_ONLY)
def project_settings(project):
    settings = settings_manager.get_project_settings_as_string(project)
    return render_template('settings/project_settings.html', project=project, settings=settings)


# ENVIRONMENTS VIEW
@webapp_bp.route("/project/<project>/environments/")
@login_required
@project_exists
@permission_required(Permissions.READ_ONLY)
def environments_view(project):
    data = environment_manager.get_environments_as_string(project)
    return render_template('environments.html', project=project, environment_data=data)


# USERS VIEW
@webapp_bp.route("/users/")
@login_required
@permission_required(Permissions.SUPER_USER)
def users_view():
    return render_template('users/users.html')


# NEW USER VIEW
@webapp_bp.route("/users/new/")
@login_required
@permission_required(Permissions.SUPER_USER)
def new_user_view():
    return render_template('users/user_form.html', edition_mode=False, edit_user=None)


# EDIT USER VIEW
@webapp_bp.route("/users/edit/<username>/")
@login_required
@permission_required(Permissions.SUPER_USER)
def edit_user_view(username):
    user = Users.get_user_by_username(username)
    return render_template('users/user_form.html', edition_mode=True, edit_user=user)


# USER PROFILE VIEW
@webapp_bp.route("/user/")
@login_required
def user_profile_view():
    return render_template('users/user_profile.html')


# LOGOUT VIEW
@webapp_bp.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect('/')
