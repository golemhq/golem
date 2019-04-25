"""Golem GUI API blueprint"""
import json
import os

from flask import jsonify, request
from flask.blueprints import Blueprint
from flask_login import login_required

from golem.core import (environment_manager, file_manager, page_object, settings_manager,
                        test_case, session, utils, tags_manager)
from golem.core import suite as suite_module
from . import gui_utils, report_parser


api_bp = Blueprint('api', __name__)


@api_bp.route("/project/get_tests/", methods=['POST'])
@login_required
def get_tests():
    if request.method == 'POST':
        project = request.form['project']
        tests = utils.get_test_cases(project)
        return json.dumps(tests)


@api_bp.route("/project/get_pages/", methods=['POST'])
@login_required
def get_pages():
    if request.method == 'POST':
        project = request.form['project']
        pages = utils.get_pages(project)
        return json.dumps(pages)


@api_bp.route("/project/get_suites/", methods=['POST'])
@login_required
def get_suite():
    if request.method == 'POST':
        project = request.form['project']
        suites = utils.get_suites(project)
        return json.dumps(suites)


@api_bp.route("/delete_element/", methods=['POST'])
@login_required
def delete_element():
    if request.method == 'POST':
        project = request.form['project']
        elem_type = request.form['elemType']
        full_path = request.form['fullPath']
        errors = utils.delete_element(project, elem_type, full_path)
        return json.dumps(errors)


@api_bp.route("/duplicate_element/", methods=['POST'])
@login_required
def duplicate_element():
    if request.method == 'POST':
        project = request.form['project']
        elem_type = request.form['elemType']
        full_path = request.form['fullPath']
        new_file_full_path = request.form['newFileFullPath']
        errors = utils.duplicate_element(project, elem_type, full_path,
                                         new_file_full_path)
        return json.dumps(errors)


@api_bp.route("/rename_element/", methods=['POST'])
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
                    error = 'Only letters, numbers and underscores are allowed'
                    break

        dir_type_name = ''
        if not error:
            if elem_type == 'test':
                dir_type_name = 'tests'
            elif elem_type == 'page':
                dir_type_name = 'pages'
            elif elem_type == 'suite':
                dir_type_name = 'suites'

            old_path = os.path.join(session.testdir, 'projects', project, dir_type_name,
                                    os.sep.join(old_parents))
            new_path = os.path.join(session.testdir, 'projects', project, dir_type_name,
                                    os.sep.join(new_parents))
            error = file_manager.rename_file(old_path, old_filename + '.py',
                                             new_path, new_filename + '.py')
        if not error and elem_type == 'test':
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
        return json.dumps(error)


@api_bp.route("/get_page_objects/", methods=['POST'])
@login_required
def get_page_objects():
    if request.method == 'POST':
        project = request.form['project']
        path = page_object.pages_base_dir(project)
        page_objects = file_manager.get_files_dot_path(path, extension='.py')
        return json.dumps(page_objects)


@api_bp.route("/get_page_contents/")
@login_required
def get_selected_page_object_elements():
    project = request.args['project']
    page = request.args['page']
    result = {
        'error': '',
        'contents': []
    }
    if not page_object.page_exists(project, page):
        result['error'] = 'page does not exist'
    else:
        result['content'] = page_object.get_page_object_content(project, page)
    return json.dumps(result)


@api_bp.route("/new_tree_element/", methods=['POST'])
@login_required
def new_tree_element():
    if request.method == 'POST':
        project = request.form['project']
        elem_type = request.form['elementType']
        is_dir = json.loads(request.form['isDir'])
        full_path = request.form['fullPath']
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
            if elem_type == 'test':
                if is_dir:
                    errors = file_manager.new_directory_of_type(project, parents,
                                                                element_name,
                                                                dir_type='tests')
                else:
                    errors = test_case.new_test_case(project, parents, element_name)
            elif elem_type == 'page':
                if is_dir:
                    errors = file_manager.new_directory_of_type(project, parents,
                                                                element_name,
                                                                dir_type='pages')
                else:
                    errors = page_object.new_page_object(project, parents, element_name)
            elif elem_type == 'suite':
                if is_dir:
                    errors = file_manager.new_directory_of_type(project, parents,
                                                                element_name,
                                                                dir_type='suites')
                else:
                    errors = suite_module.new_suite(project, parents, element_name)
        element = {
            'name': element_name,
            'full_path': dot_path,
            'type': elem_type,
            'is_directory': is_dir
        }
        return json.dumps({'errors': errors, 'project_name': project,
                           'element': element})


@api_bp.route("/new_project/", methods=['POST'])
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
        elif utils.project_exists(project_name):
            errors.append('A project with that name already exists')
        else:
            utils.create_new_project(project_name)
        return json.dumps({'errors': errors, 'project_name': project_name})


@api_bp.route("/save_test_case_code/", methods=['POST'])
@login_required
def save_test_case_code():
    if request.method == 'POST':
        project = request.json['project']
        test_case_name = request.json['testCaseName']
        table_test_data = request.json['testData']
        content = request.json['content']
        test_case.save_test_case_code(project, test_case_name, content,
                                      table_test_data)
        path = test_case.test_file_path(project, test_case_name)
        _, error = utils.import_module(path)
        return json.dumps({'error': error})


@api_bp.route("/get_golem_actions/", methods=['GET'])
@login_required
def get_golem_actions():
    global_actions = gui_utils.Golem_action_parser().get_actions()
    response = jsonify(global_actions)
    response.cache_control.max_age = 60 * 60
    response.cache_control.public = True
    return response


@api_bp.route("/save_page_object/", methods=['POST'])
@login_required
def save_page_object():
    if request.method == 'POST':
        project = request.json['project']
        page_object_name = request.json['pageObjectName']
        elements = request.json['elements']
        functions = request.json['functions']
        import_lines = request.json['importLines']
        page_object.save_page_object(project, page_object_name,
                                     elements, functions, import_lines)
        return json.dumps('ok')


@api_bp.route("/save_page_object_code/", methods=['POST'])
@login_required
def save_page_object_code():
    if request.method == 'POST':
        project = request.json['project']
        page_object_name = request.json['pageObjectName']
        content = request.json['content']
        path = page_object.page_file_path(project, page_object_name)
        page_object.save_page_object_code(project, page_object_name, content)
        _, error = utils.import_module(path)
        return json.dumps({'error': error})


@api_bp.route("/run_test_case/", methods=['POST'])
@login_required
def run_test_case():
    if request.method == 'POST':
        project = request.json['project']
        test_name = request.json['testName']
        browsers = request.json['browsers']
        environments = request.json['environments']
        processes = request.json['processes']
        timestamp = gui_utils.run_test_case(project, test_name, browsers, environments,
                                            processes)
        return json.dumps(timestamp)


@api_bp.route("/save_test_case/", methods=['POST'])
@login_required
def save_test_case():
    if request.method == 'POST':
        project = request.json['project']
        test_name = request.json['testCaseName']
        description = request.json['description']
        page_objects = request.json['pageObjects']
        test_data_content = request.json['testData']
        test_steps = request.json['testSteps']
        tags = request.json['tags']
        test_case.save_test_case(project, test_name, description, page_objects,
                                 test_steps, test_data_content, tags)
        return json.dumps('ok')


@api_bp.route("/check_test_case_run_result/", methods=['POST'])
@login_required
def check_test_case_run_result():
    if request.method == 'POST':
        project = request.form['project']
        test_case_name = request.form['testCaseName']
        timestamp = request.form['timestamp']
        path = os.path.join(session.testdir, 'projects', project, 'reports',
                            'single_tests', test_case_name, timestamp)
        sets = {}
        result = {
            'sets': {},
            'is_finished': False
        }
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
                test_case_data = report_parser.get_test_case_data(project,
                                                                  test_case_name,
                                                                  execution=timestamp,
                                                                  test_set=set_name,
                                                                  is_single=True)
                sets[set_name]['report'] = test_case_data
            log_path = os.path.join(path, set_name, 'execution_info.log')
            if os.path.exists(log_path):
                with open(log_path) as log_file:
                    sets[set_name]['log'] = log_file.readlines()
        result['sets'] = sets
        return json.dumps(result)


@api_bp.route("/report/get_test_set_detail/", methods=['GET'])
@login_required
def get_test_set_detail():
    project = request.args['project']
    suite = request.args['suite']
    execution = request.args['execution']
    test_full_name = request.args['testFullName']
    test_set = request.args['testSet']

    test_detail = report_parser.get_test_case_data(project, test_full_name,
                                                   suite=suite, execution=execution,
                                                   test_set=test_set, is_single=False,
                                                   encode_screenshots=True)
    response = jsonify(test_detail)
    if test_detail['has_finished']:
        response.cache_control.max_age = 60 * 60 * 100
        response.cache_control.public = True
    return response


@api_bp.route("/run_suite/", methods=['POST'])
@login_required
def run_suite():
    if request.method == 'POST':
        project = request.form['project']
        suite_name = request.form['suite']
        timestamp = gui_utils.run_suite(project, suite_name)
        return json.dumps(timestamp)


@api_bp.route("/save_suite/", methods=['POST'])
@login_required
def save_suite():
    if request.method == 'POST':
        project = request.json['project']
        suite_name = request.json['suite']
        test_cases = request.json['testCases']
        processes = request.json['processes']
        tags = request.json['tags']
        browsers = request.json['browsers']
        environments = request.json['environments']
        suite_module.save_suite(project, suite_name, test_cases, processes, browsers,
                                environments, tags)
        return json.dumps('ok')


@api_bp.route("/save_settings/", methods=['POST'])
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
        settings_manager.save_global_settings(global_settings)
        session.settings = settings_manager.get_global_settings()
        if project_settings:
            settings_manager.save_project_settings(project, project_settings)
            # re-read project settings
            session.settings = settings_manager.get_project_settings(project)
        return json.dumps(result)


@api_bp.route("/save_environments/", methods=['POST'])
@login_required
def save_environments():
    if request.method == 'POST':
        project = request.json['project']
        env_data = request.json['environmentData']
        error = environment_manager.save_environments(project, env_data)
        return json.dumps(error)


@api_bp.route("/get_supported_browsers/", methods=['GET'])
@login_required
def get_supported_browsers():
    project = request.args['project']
    settings = settings_manager.get_project_settings(project)
    remote_browsers = settings_manager.get_remote_browser_list(settings)
    default_browsers = gui_utils.get_supported_browsers_suggestions()
    return json.dumps(remote_browsers + default_browsers)


@api_bp.route("/get_environments/", methods=['GET'])
@login_required
def get_environments():
    project = request.args['project']
    return json.dumps(environment_manager.get_envs(project))


@api_bp.route("/report/get_last_executions/", methods=['POST'])
@login_required
def get_last_executions():
    if request.method == 'POST':
        projects = request.json['projects']
        suite = request.json['suite']
        limit = request.json['limit']
        project_data = report_parser.get_last_executions(projects, suite, limit)
        return jsonify(projects=project_data)


@api_bp.route("/report/get_execution_data/", methods=['GET'])
@login_required
def get_execution_data():
    if request.method == 'GET':
        project = request.args['project']
        suite = request.args['suite']
        execution = request.args['execution']
        execution_data = report_parser.get_execution_data(project=project, suite=suite,
                                                          execution=execution)
        response = jsonify(execution_data)
        if execution_data['has_finished']:
            response.cache_control.max_age = 60 * 60 * 24 * 5
            response.cache_control.public = True
        return response


@api_bp.route("/report/get_project_health_data/", methods=['POST'])
@login_required
def get_project_health_data():
    if request.method == 'POST':
        project = request.form['project']
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


@api_bp.route("/page/page_exists/", methods=['POST'])
@login_required
def page_exists():
    if request.method == 'POST':
        project = request.form['project']
        full_page_name = request.form['fullPageName']
        page_exists = page_object.page_exists(project, full_page_name)
        return jsonify(page_exists)


@api_bp.route("/get_amount_of_tests/", methods=['GET'])
@login_required
def get_amount_of_tests():
    project = request.args['project']
    tests = utils.get_directory_tests(project, '')
    amount = len(tests)
    response = jsonify(amount)
    if amount > 0:
        response.cache_control.max_age = 108000
        response.cache_control.public = True
    return response


@api_bp.route("/get_default_browser/", methods=['GET'])
@login_required
def get_default_browser():
    return jsonify(session.settings['default_browser'])


@api_bp.route("/project/tests/tags/", methods=['POST'])
@login_required
def get_project_tests_tags():
    project = request.form['project']
    tags = tags_manager.get_all_project_tests_tags(project)
    return jsonify(tags)


@api_bp.route("/project/tags/", methods=['POST'])
@login_required
def get_project_tags():
    project = request.form['project']
    tags = tags_manager.get_project_unique_tags(project)
    return jsonify(tags)

