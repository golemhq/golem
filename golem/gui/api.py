"""Golem GUI API blueprint"""
import os
from copy import deepcopy
from functools import wraps

from flask import jsonify, request, current_app, abort
from flask.blueprints import Blueprint
from flask_login import current_user
from itsdangerous import BadSignature, SignatureExpired

from golem.core import (environment_manager, file_manager, page_object, settings_manager,
                        test_case, session, utils, tags_manager, test_directory)
from golem.core import suite as suite_module
from golem.core.project import Project, create_project
from golem.gui import gui_utils, report_parser
from golem.gui.user_management import Users, Permissions


api_bp = Blueprint('api', __name__, url_prefix='/api')


def auth_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            token = request.headers.get('token', None)
            if token:
                try:
                    user = Users.verify_auth_token(current_app.secret_key, token)
                    request.api_user = user
                except BadSignature:
                    abort(401, 'Token did not match')
                except SignatureExpired:
                    abort(401, 'Signature Expired')
                except Exception:
                    abort(401, 'Unknown error')
            else:
                abort(400, 'Missing token')
        return func(*args, **kwargs)
    return decorated_view


@api_bp.route('/auth/token', methods=['POST'])
def auth_token():
    username = request.json['username']
    password = request.json['password']
    user = Users.get_user_by_username(username=username)
    if user is None:
        abort(401, 'User does not exist')
    elif not user.verify_password(password):
        abort(401, 'Incorrect password')
    else:
        token = user.generate_auth_token(current_app.secret_key)
        return jsonify(token.decode())


@api_bp.route('/golem/actions')
@auth_required
def golem_actions():
    response = jsonify(gui_utils.Golem_action_parser().get_actions())
    response.cache_control.max_age = 604800
    response.cache_control.public = True
    return response


@api_bp.route('/golem/default-browser')
@auth_required
def golem_default_browser():
    return jsonify(session.settings['default_browser'])


@api_bp.route('/golem/project-permissions')
@auth_required
def golem_permissions_project():
    return jsonify(Permissions.project_permissions)


@api_bp.route('/page/code/save', methods=['PUT'])
@auth_required
def page_code_save():
    project = request.json['project']
    page_object_name = request.json['pageName']
    content = request.json['content']
    _verify_permissions(Permissions.STANDARD, project)
    path = page_object.page_file_path(project, page_object_name)
    page_object.save_page_object_code(project, page_object_name, content)
    _, error = utils.import_module(path)
    return jsonify({'error': error})


@api_bp.route('/page/delete', methods=['DELETE'])
@auth_required
def page_delete():
    project = request.json['project']
    full_path = request.json['fullPath']
    _verify_permissions(Permissions.ADMIN, project)
    errors = utils.delete_element(project, 'page', full_path)
    return jsonify(errors)


@api_bp.route('/page/duplicate', methods=['POST'])
@auth_required
def page_duplicate():
    project = request.json['project']
    full_path = request.json['fullPath']
    new_file_full_path = request.json['newFileFullPath']
    _verify_permissions(Permissions.STANDARD, project)
    errors = utils.duplicate_element(project, 'page', full_path, new_file_full_path)
    return jsonify(errors)


@api_bp.route('/page/elements')
@auth_required
def page_elements():
    project = request.args['project']
    page = request.args['page']
    _verify_permissions(Permissions.READ_ONLY, project)
    result = {
        'error': '',
        'contents': []
    }
    if not page_object.page_exists(project, page):
        result['error'] = 'page does not exist'
    else:
        result['content'] = page_object.get_page_object_content(project, page)
    return jsonify(result)


@api_bp.route('/page/rename', methods=['POST'])
@auth_required
def page_rename():
    project = request.json['project']
    full_filename = request.json['fullFilename']
    new_full_filename = request.json['newFullFilename']
    _verify_permissions(Permissions.STANDARD, project)
    error = _rename_element(project, full_filename, new_full_filename, 'page')
    return jsonify({'error': error})


@api_bp.route('/page/save', methods=['PUT'])
@auth_required
def page_save():
    project = request.json['project']
    page_object_name = request.json['pageName']
    elements = request.json['elements']
    functions = request.json['functions']
    import_lines = request.json['importLines']
    _verify_permissions(Permissions.STANDARD, project)
    page_object.save_page_object(project, page_object_name, elements, functions,
                                 import_lines)
    return jsonify('page-saved')


@api_bp.route('/project', methods=['POST'])
@auth_required
def project_create():
    project_name = request.json['project']
    project_name = project_name.strip().replace(' ', '_')
    _verify_permissions(Permissions.SUPER_USER)
    errors = []
    if len(project_name) < 3:
        errors.append('Project name is too short')
    elif len(project_name) > 50:
        errors.append('Project name is too long')
    elif test_directory.project_exists(project_name):
        errors.append('A project with that name already exists')
    else:
        create_project(project_name)
    return jsonify({'errors': errors, 'project_name': project_name})


@api_bp.route('/project/environments')
@auth_required
def project_environments():
    project = request.args['project']
    _verify_permissions(Permissions.READ_ONLY, project)
    return jsonify(environment_manager.get_envs(project))


@api_bp.route('/project/environments/save', methods=['PUT'])
@auth_required
def project_environments_save():
    project = request.json['project']
    env_data = request.json['environmentData']
    _verify_permissions(Permissions.ADMIN, project)
    error = environment_manager.save_environments(project, env_data)
    return jsonify({'error': error})


@api_bp.route('/project-exists')
@auth_required
def project_exists():
    project = request.json['project']
    return jsonify(test_directory.project_exists(project))


@api_bp.route('/project/has-tests')
@auth_required
def project_has_tests():
    project = request.args['project']
    has_tests = Project(project).has_tests
    response = jsonify(has_tests)
    if has_tests:
        response.cache_control.max_age = 604800
        response.cache_control.public = True
    return response


@api_bp.route('/project/health')
@auth_required
def project_health():
    project = request.args['project']
    _verify_permissions(Permissions.REPORTS_ONLY, project)
    project_data = report_parser.get_last_executions(projects=[project], suite=None,
                                                     limit=1)
    health_data = {}
    for suite, executions in project_data[project].items():
        execution_data = report_parser.get_execution_data(project=project,
                                                          suite=suite,
                                                          execution=executions[0])
        health_data[suite] = {
            'execution': executions[0],
            'total': execution_data['total_tests'],
            'totals_by_result': execution_data['totals_by_result']
        }
    return jsonify(health_data)


@api_bp.route('/project/page', methods=['POST'])
@auth_required
def project_page_create():
    project = request.json['project']
    is_dir = request.json['isDir']
    full_path = request.json['fullPath']
    _verify_permissions(Permissions.STANDARD, project)
    element, errors = _create_project_element(project, 'page', full_path, is_dir)
    return jsonify({'errors': errors, 'element': element})


@api_bp.route('/project/page-exists')
@auth_required
def project_page_exists():
    project = request.args['project']
    page_name = request.args['page']
    _verify_permissions(Permissions.READ_ONLY, project)
    return jsonify(page_object.page_exists(project, page_name))


@api_bp.route('/project/page-tree')
@auth_required
def project_page_tree():
    project = request.args['project']
    _verify_permissions(Permissions.READ_ONLY, project)
    return jsonify(Project(project).page_tree)


@api_bp.route('/project/pages')
@auth_required
def project_pages():
    project = request.args['project']
    _verify_permissions(Permissions.READ_ONLY, project)
    path = page_object.pages_base_dir(project)
    page_objects = file_manager.get_files_dot_path(path, extension='.py')
    return jsonify(page_objects)


@api_bp.route('/project/suite', methods=['POST'])
@auth_required
def project_suite_create():
    project = request.json['project']
    is_dir = request.json['isDir']
    full_path = request.json['fullPath']
    _verify_permissions(Permissions.STANDARD, project)
    element, errors = _create_project_element(project, 'suite', full_path, is_dir)
    return jsonify({'errors': errors, 'element': element})


@api_bp.route('/project/suite-tree')
@auth_required
def project_suite_tree():
    project = request.args['project']
    _verify_permissions(Permissions.READ_ONLY, project)
    return jsonify(Project(project).suite_tree)


@api_bp.route('/project/supported-browsers')
@auth_required
def project_supported_browsers():
    project = request.args['project']
    _verify_permissions(Permissions.READ_ONLY, project)
    settings = settings_manager.get_project_settings(project)
    remote_browsers = settings_manager.get_remote_browser_list(settings)
    default_browsers = gui_utils.get_supported_browsers_suggestions()
    return jsonify(remote_browsers + default_browsers)


@api_bp.route('/project/tags')
@auth_required
def project_tags():
    project = request.args['project']
    _verify_permissions(Permissions.READ_ONLY, project)
    return jsonify(tags_manager.get_project_unique_tags(project))


@api_bp.route('/project/test', methods=['POST'])
@auth_required
def project_test_create():
    project = request.json['project']
    is_dir = request.json['isDir']
    full_path = request.json['fullPath']
    _verify_permissions(Permissions.STANDARD, project)
    element, errors = _create_project_element(project, 'test', full_path, is_dir)
    return jsonify({'errors': errors, 'element': element})


@api_bp.route('/project/test-tags')
@auth_required
def project_test_tags():
    project = request.args['project']
    _verify_permissions(Permissions.READ_ONLY, project)
    return jsonify(tags_manager.get_all_project_tests_tags(project))


@api_bp.route('/project/test-tree')
@auth_required
def project_test_tree():
    project = request.args['project']
    _verify_permissions(Permissions.READ_ONLY, project)
    return jsonify(Project(project).test_tree)


@api_bp.route('/projects')
@auth_required
def projects():
    return jsonify(test_directory.get_projects())


@api_bp.route('/report/suite/execution')
@auth_required
def report_suite_execution():
    project = request.args['project']
    suite = request.args['suite']
    execution = request.args['execution']
    _verify_permissions(Permissions.REPORTS_ONLY, project)
    execution_data = report_parser.get_execution_data(project=project, suite=suite,
                                                      execution=execution)
    response = jsonify(execution_data)
    if execution_data['has_finished']:
        response.cache_control.max_age = 60 * 60 * 24 * 7
        response.cache_control.public = True
    return response


@api_bp.route('/report/last-executions')
@auth_required
def report_last_executions():
    user = _get_user_api_or_session()
    project_list = user.project_list
    project_data = report_parser.get_last_executions(project_list, limit=5)
    return jsonify(projects=project_data)


@api_bp.route('/report/project/last-executions')
@auth_required
def report_project_last_executions():
    project = request.args['project']
    _verify_permissions(Permissions.REPORTS_ONLY, project)
    project_data = report_parser.get_last_executions([project], limit=10)
    return jsonify(projects=project_data)


@api_bp.route('/report/suite/last-executions')
@auth_required
def report_suite_last_executions():
    project = request.args['project']
    suite = request.args['suite']
    _verify_permissions(Permissions.REPORTS_ONLY, project)
    project_data = report_parser.get_last_executions([project], suite=suite, limit=50)
    return jsonify(projects=project_data)


@api_bp.route('/report/test-set')
@auth_required
def report_test_set():
    project = request.args['project']
    suite = request.args['suite']
    execution = request.args['execution']
    test_full_name = request.args['testName']
    test_set = request.args['testSet']
    _verify_permissions(Permissions.REPORTS_ONLY, project)
    test_detail = report_parser.get_test_case_data(project, test_full_name,
                                                   suite=suite, execution=execution,
                                                   test_set=test_set, is_single=False,
                                                   encode_screenshots=True)
    response = jsonify(test_detail)
    if test_detail['has_finished']:
        response.cache_control.max_age = 604800
        response.cache_control.public = True
    return response


@api_bp.route('/report/test/status')
@auth_required
def report_test_status():
    project = request.args['project']
    test_case_name = request.args['test']
    timestamp = request.args['timestamp']
    _verify_permissions(Permissions.REPORTS_ONLY, project)
    path = os.path.join(session.testdir, 'projects', project, 'reports',
                        'single_tests', test_case_name, timestamp)
    result = {
        'sets': {},
        'is_finished': False
    }
    sets = {}
    if os.path.isdir(path):
        for elem in os.listdir(path):
            if os.path.isdir(os.path.join(path, elem)):
                sets[elem] = {
                    'log': [],
                    'report': None
                }
    result['is_finished'] = report_parser.is_execution_finished(path, sets)
    for set_name in sets:
        report_path = os.path.join(path, set_name, 'report.json')
        if os.path.exists(report_path):
            test_case_data = report_parser.get_test_case_data(project, test_case_name,
                                                              execution=timestamp,
                                                              test_set=set_name,
                                                              is_single=True)
            sets[set_name]['report'] = test_case_data
        log_path = os.path.join(path, set_name, 'execution_info.log')
        if os.path.exists(log_path):
            with open(log_path) as log_file:
                sets[set_name]['log'] = log_file.readlines()
    result['sets'] = sets
    return jsonify(result)


@api_bp.route('/settings/global/save', methods=['PUT'])
@auth_required
def settings_global_save():
    settings = request.json['settings']
    _verify_permissions(Permissions.SUPER_USER)
    settings_manager.save_global_settings(settings)
    session.settings = settings_manager.get_global_settings()
    return jsonify('settings-saved')


@api_bp.route('/settings/global')
@auth_required
def settings_global_get():
    _verify_permissions(Permissions.SUPER_USER)
    return jsonify(settings_manager.get_global_settings())


@api_bp.route('/settings/project/save', methods=['PUT'])
@auth_required
def settings_project_save():
    project = request.json['project']
    settings = request.json['settings']
    _verify_permissions(Permissions.ADMIN, project)
    settings_manager.save_project_settings(project, settings)
    return jsonify('settings-saved')


@api_bp.route('/settings/project')
@auth_required
def settings_project_get():
    project = request.args['project']
    _verify_permissions(Permissions.READ_ONLY, project)
    return jsonify(settings_manager.get_project_settings_only(project))


@api_bp.route('/suite/delete', methods=['DELETE'])
@auth_required
def suite_delete():
    project = request.json['project']
    full_path = request.json['fullPath']
    _verify_permissions(Permissions.ADMIN, project)
    errors = utils.delete_element(project, 'suite', full_path)
    return jsonify(errors)


@api_bp.route('/suite/duplicate', methods=['POST'])
@auth_required
def suite_duplicate():
    project = request.json['project']
    full_path = request.json['fullPath']
    new_file_full_path = request.json['newFileFullPath']
    _verify_permissions(Permissions.STANDARD, project)
    errors = utils.duplicate_element(project, 'suite', full_path, new_file_full_path)
    return jsonify(errors)


@api_bp.route('/suite/rename', methods=['POST'])
@auth_required
def suite_rename():
    project = request.json['project']
    full_filename = request.json['fullFilename']
    new_full_filename = request.json['newFullFilename']
    _verify_permissions(Permissions.STANDARD, project)
    error = _rename_element(project, full_filename, new_full_filename, 'suite')
    return jsonify({'error': error})


@api_bp.route('/suite/run', methods=['POST'])
@auth_required
def suite_run():
    project = request.json['project']
    suite_name = request.json['suite']
    _verify_permissions(Permissions.STANDARD, project)
    timestamp = gui_utils.run_suite(project, suite_name)
    return jsonify(timestamp)


@api_bp.route('/suite/save', methods=['PUT'])
@auth_required
def suite_save():
    project = request.json['project']
    suite_name = request.json['suite']
    test_cases = request.json['tests']
    processes = request.json['processes']
    tags = request.json['tags']
    browsers = request.json['browsers']
    environments = request.json['environments']
    _verify_permissions(Permissions.STANDARD, project)
    suite_module.save_suite(project, suite_name, test_cases, processes, browsers,
                            environments, tags)
    return jsonify('suite-saved')


@api_bp.route('/test/code/save', methods=['PUT'])
@auth_required
def test_code_save():
    project = request.json['project']
    test_case_name = request.json['testName']
    table_test_data = request.json['testData']
    content = request.json['content']
    _verify_permissions(Permissions.STANDARD, project)
    test_case.save_test_case_code(project, test_case_name, content, table_test_data)
    path = test_case.test_file_path(project, test_case_name)
    _, error = utils.import_module(path)
    return jsonify({'error': error})


@api_bp.route('/test/delete', methods=['DELETE'])
@auth_required
def test_delete():
    project = request.json['project']
    full_path = request.json['fullPath']
    _verify_permissions(Permissions.ADMIN, project)
    errors = utils.delete_element(project, 'test', full_path)
    return jsonify(errors)


@api_bp.route('/test/duplicate', methods=['POST'])
@auth_required
def test_duplicate():
    project = request.json['project']
    full_path = request.json['fullPath']
    new_file_full_path = request.json['newFileFullPath']
    _verify_permissions(Permissions.STANDARD, project)
    errors = utils.duplicate_element(project, 'test', full_path, new_file_full_path)
    return jsonify(errors)


@api_bp.route('/test/rename', methods=['POST'])
@auth_required
def test_rename():
    project = request.json['project']
    full_filename = request.json['fullFilename']
    new_full_filename = request.json['newFullFilename']
    _verify_permissions(Permissions.STANDARD, project)
    error = _rename_element(project, full_filename, new_full_filename, 'test')
    return jsonify({'error': error})


@api_bp.route('/test/run', methods=['POST'])
@auth_required
def test_run():
    project = request.json['project']
    test_name = request.json['testName']
    browsers = request.json['browsers']
    environments = request.json['environments']
    processes = request.json['processes']
    _verify_permissions(Permissions.STANDARD, project)
    timestamp = gui_utils.run_test_case(project, test_name, browsers, environments,
                                        processes)
    return jsonify(timestamp)


@api_bp.route('/test/save', methods=['PUT'])
@auth_required
def test_save():
    project = request.json['project']
    test_name = request.json['testName']
    description = request.json['description']
    page_objects = request.json['pages']
    test_data_content = request.json['testData']
    test_steps = request.json['steps']
    tags = request.json['tags']
    _verify_permissions(Permissions.STANDARD, project)
    test_case.save_test_case(project, test_name, description, page_objects,
                             test_steps, test_data_content, tags)
    return jsonify('test-saved')


@api_bp.route('/users')
@auth_required
def users_get():
    _verify_permissions(Permissions.SUPER_USER)
    users = deepcopy(Users.users())
    for user in users:
        del user['password']
    return jsonify(users)


@api_bp.route('/users/user')
@auth_required
def user_get():
    _verify_permissions(Permissions.SUPER_USER)
    username = request.args['username']
    user = Users.get_user_dictionary(username)
    if user:
        del user['password']
    return jsonify(user)


@api_bp.route('/users/new', methods=['PUT'])
@auth_required
def users_new():
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']
    is_superuser = request.json['isSuperuser']
    _verify_permissions(Permissions.SUPER_USER)
    project_permissions_raw = request.json['projectPermissions']
    project_permissions = {}
    for project_permission in project_permissions_raw:
        project_permissions[project_permission['project']] = project_permission['permission']
    errors = Users.create_user(username, password, email, is_superuser, project_permissions)
    return jsonify(errors)


@api_bp.route('/users/edit', methods=['POST'])
@auth_required
def users_edit():
    old_username = request.json['oldUsername']
    new_username = request.json['newUsername']
    email = request.json['email']
    is_superuser = request.json['isSuperuser']
    project_permissions_raw = request.json['projectPermissions']
    _verify_permissions(Permissions.SUPER_USER)
    project_permissions = {}
    if project_permissions_raw is not None:
        for p in project_permissions_raw:
            project_permissions[p['project']] = p['permission']
    errors = Users.edit_user(old_username, new_username, email, is_superuser, project_permissions)
    return jsonify(errors)


@api_bp.route('/users/delete', methods=['DELETE'])
@auth_required
def users_delete():
    _verify_permissions(Permissions.SUPER_USER)
    username = request.json['username']
    errors = Users.delete_user(username)
    return jsonify({'errors': errors})


@api_bp.route('/users/reset-password', methods=['POST'])
@auth_required
def users_reset_user_pasword():
    _verify_permissions(Permissions.SUPER_USER)
    username = request.json['username']
    new_password = request.json['newPassword']
    errors = Users.reset_user_password(username, new_password)
    return jsonify({'errors': errors})


@api_bp.route('/user/reset-password', methods=['POST'])
@auth_required
def user_reset_user_pasword():
    username = request.json['username']
    if username == current_user.username:
        new_password = request.json['newPassword']
        errors = Users.reset_user_password(username, new_password)
    else:
        errors = ['Cannot change current user password']
    return jsonify({'errors': errors})


def _rename_element(project, filename, new_filename, element_type):
    error = ''
    old_filename, old_parents = utils.separate_file_from_parents(filename)
    new_filename, new_parents = utils.separate_file_from_parents(new_filename)

    if len(new_filename) == 0:
        error = 'File name cannot be empty'
    else:
        for c in new_filename.replace('.', ''):
            if not c.isalnum() and c not in ['-', '_']:
                error = 'Only letters, numbers and underscores are allowed'
                break

    dir_type_name = ''
    if not error:
        if element_type == 'test':
            dir_type_name = 'tests'
        elif element_type == 'page':
            dir_type_name = 'pages'
        elif element_type == 'suite':
            dir_type_name = 'suites'

        old_path = os.path.join(session.testdir, 'projects', project, dir_type_name,
                                os.sep.join(old_parents))
        new_path = os.path.join(session.testdir, 'projects', project, dir_type_name,
                                os.sep.join(new_parents))
        error = file_manager.rename_file(old_path, old_filename + '.py',
                                         new_path, new_filename + '.py')
    if not error and element_type == 'test':
        # try to rename data file in /data/ folder
        # TODO, data files in /data/ will be deprecated
        old_path = os.path.join(session.testdir, 'projects', project, 'data',
                                os.sep.join(old_parents))
        new_path = os.path.join(session.testdir, 'projects', project, 'data',
                                os.sep.join(new_parents))
        if os.path.isfile(os.path.join(old_path, old_filename + '.csv')):
            error = file_manager.rename_file(old_path, old_filename + '.csv',
                                             new_path, new_filename + '.csv')
        # try to rename data file in /tests/ folder
        old_path = os.path.join(session.testdir, 'projects', project, 'tests',
                                os.sep.join(old_parents))
        new_path = os.path.join(session.testdir, 'projects', project, 'tests',
                                os.sep.join(new_parents))
        if os.path.isfile(os.path.join(old_path, old_filename + '.csv')):
            error = file_manager.rename_file(old_path, old_filename + '.csv',
                                             new_path, new_filename + '.csv')
    return error


def _create_project_element(project, element_type, full_path, is_dir):
    full_path = full_path.replace(' ', '_')
    dot_path = full_path
    errors = []
    full_path = full_path.split('.')
    element_name = full_path.pop()
    parents = full_path
    # verify that the string only contains letters, numbers or underscores
    if len(element_name) == 0:
        errors.append('Name cannot be empty')
    else:
        for c in element_name:
            if not c.isalnum() and c != '_':
                errors.append('Only letters, numbers and underscores are allowed')
                break
    if not errors:
        if element_type == 'test':
            if is_dir:
                errors = file_manager.new_directory_of_type(project, parents,
                                                            element_name,
                                                            dir_type='tests')
            else:
                errors = test_case.new_test_case(project, parents, element_name)
        elif element_type == 'page':
            if is_dir:
                errors = file_manager.new_directory_of_type(project, parents,
                                                            element_name,
                                                            dir_type='pages')
            else:
                errors = page_object.new_page_object(project, parents, element_name)
        elif element_type == 'suite':
            if is_dir:
                errors = file_manager.new_directory_of_type(project, parents,
                                                            element_name,
                                                            dir_type='suites')
            else:
                errors = suite_module.new_suite(project, parents, element_name)
    element = {
        'name': element_name,
        'full_path': dot_path,
        'type': element_type,
        'is_directory': is_dir
    }
    return element, errors


def _get_user_api_or_session():
    """Get current_user if user is authenticated (Flask Login)
    or request.api_user if present
    """
    user = None
    if current_user and current_user.is_authenticated:
        user = current_user
    elif request.api_user:
        user = request.api_user
    return user


def _verify_permissions(permission, project=None):
    """Verify session user or api user has the required permissions.
    For permission=superuser, project is optional.
    When permission weight is not reached it will raise HTTP 401.
    """
    user = _get_user_api_or_session()
    if user is None:
        abort(401)
    required_permission_weight = Permissions.get_weight(permission)
    user_weight = 0
    if user.is_superuser:
        user_weight = Permissions.get_weight(Permissions.SUPER_USER)
    elif project:
        user_weight = user.project_weight(project)
    if required_permission_weight > user_weight:
        abort(401)
