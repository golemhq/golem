"""Helper general purpose functions"""
import csv
import importlib
import shutil
import json
import os
import sys
import uuid
import traceback
from ast import literal_eval
from datetime import datetime

import golem
from golem.core import settings_manager
from golem.core import file_manager


def get_test_cases(workspace, project):
    path = os.path.join(workspace, 'projects', project, 'tests')
    test_cases = file_manager.generate_file_structure_dict(path)
    return test_cases


def get_pages(workspace, project):
    path = os.path.join(workspace, 'projects', project, 'pages')
    pages = file_manager.generate_file_structure_dict(path)
    return pages


def get_suites(workspace, project):
    path = os.path.join(workspace, 'projects', project, 'suites')
    suites = file_manager.generate_file_structure_dict(path)
    return suites


def get_projects(workspace):
    projects = []
    path = os.path.join(workspace, 'projects')
    projects = next(os.walk(path))[1]
    projects = [x for x in projects if x != '__pycache__']
    return projects


def project_exists(workspace, project):
    return project in get_projects(workspace)


def get_directory_test_cases(workspace, project, suite):
    '''Return a list with all the test cases of a given directory'''
    tests = list()
    path = os.path.join(workspace, 'projects', project, 'tests', suite)
    files = file_manager.get_files_dot_path(path, extension='.py')
    tests = ['.'.join((suite, x)) for x in files]
    return tests


def get_timestamp():
    time_format = "%Y.%m.%d.%H.%M.%S.%f"
    timestamp = datetime.today().strftime(time_format)
    # remove last 3 decimal places from microseconds
    timestamp = timestamp[:-3]
    return timestamp


def get_date_from_timestamp(timestamp):
    date = datetime.strptime(timestamp, '%Y.%m.%d.%H.%M.%S.%f')
    return date


def display_tree_structure_command_line(structure, lvl=0):
    """Displays a directory tree structure to the command line"""
    for element in structure:
        if element['type'] == 'file':
            print('{}{}'.format(' ' * lvl * 2, element['name']))
        else:
            print('{}{}/'.format(' ' * lvl * 2, element['name']))
            display_tree_structure_command_line(element['sub_elements'], lvl + 1)


def separate_file_from_parents(full_filename):
    """Receives a full filename with parents (separated by dots)
    Returns a duple, first element is the filename and second element
    is the list of parents that might be empty"""
    splitted = full_filename.split('.')
    file = splitted.pop()
    parents = splitted
    return (file, parents)


def is_first_level_directory(workspace, project, directory):
    path = os.path.join(workspace, 'projects', project, 'tests', directory)
    return os.path.isdir(path)


def create_new_project(workspace, project):
    file_manager.create_directory(path_list=[workspace,'projects',project],
                                      add_init=True)
    # TODO, remove, don't create data folder for new projects
    # create_directory(path_list=[workspace, 'projects', project, 'data'], add_init=False)
    path_list = [workspace, 'projects', project, 'pages']
    file_manager.create_directory(path_list=path_list, add_init=True)
    path_list = [workspace, 'projects', project, 'reports']
    file_manager.create_directory(path_list=path_list, add_init=False)
    path_list = [workspace, 'projects', project, 'tests']
    file_manager.create_directory(path_list=path_list, add_init=True)
    path_list = [workspace, 'projects', project, 'suites']
    file_manager.create_directory(path_list=path_list, add_init=True)
    extend_path = os.path.join(workspace, 'projects', project, 'extend.py')
    open(extend_path, 'a').close()

    settings_manager.create_project_settings_file(workspace, project)

    environments_path = os.path.join(workspace, 'projects', project, 'environments.json')
    with open(environments_path, 'a') as environments_file:
        environments_file.write('{}')
    print('Project {} created'.format(project))


def create_test_dir(workspace):
    file_manager.create_directory(path_list=[workspace], add_init=True)
    file_manager.create_directory(path_list=[workspace, 'projects'],
                                  add_init=True)
    file_manager.create_directory(path_list=[workspace, 'drivers'],
                                  add_init=False)

    golem_start_py_content = ("import os\n\n"
                              "from golem.main import execute_from_command_line"
                              "\n\n"
                              "if __name__ == '__main__':\n"
                              "    execute_from_command_line(os.getcwd())\n")
    golem_start_py_path = os.path.join(workspace, 'golem_start.py')
    with open(golem_start_py_path, 'a') as golem_start_py_file:
        golem_start_py_file.write(golem_start_py_content)

    settings_manager.create_global_settings_file(workspace)

    users_path = os.path.join(workspace, 'users.json')
    open(users_path, 'a').close()
    create_user(workspace, 'admin', 'admin', True, ["*"], ["*"])

    print('New golem test directory created at {}'.format(workspace))
    print('Use credentials to access the GUI module:')
    print('user: admin')
    print('password: admin')


def create_user(workspace, username, password, is_admin, projects, reports):
    errors = []
    with open(os.path.join(workspace, 'users.json')) as users_file:
        try:
            user_data = json.load(users_file)
        except:
            user_data = []
    for user in user_data:
        if user['username'] == username:
            errors.append('username {} already exists'.format(username))
            break
    if not errors:
        new_user = {
            'id': str(uuid.uuid4())[:8],
            'username': username,
            'password': password,
            'is_admin': is_admin,
            'gui_projects': projects,
            'report_projects': reports
        }
        user_data.append(new_user)
        with open(os.path.join(workspace, 'users.json'), 'w') as users_file:
            json.dump(user_data, users_file, indent=4)

    return errors


def delete_element(workspace, project, element_type, dot_path):
    """Delete a test, page or suite given it's full path
    separated by dots.
    """
    if element_type == 'test':
        folder = 'tests'
    elif element_type == 'page':
        folder = 'pages'
    elif element_type == 'suite':
        folder = 'suites'
    else:
        raise Exception('Incorrect element type')

    errors = []
    path = os.path.join(workspace, 'projects', project, folder,
                        dot_path.replace('.', os.sep) + '.py')
    if not os.path.exists(path):
        errors.append('File {} does not exist'.format(dot_path))
    else:
        try:
            os.remove(path)
        except:
            errors.append('There was an error removing file {}'.format(dot_path))

    if element_type == 'test':
        # TODO deprecate data folder
        data_path = os.path.join(workspace, 'projects', project, 'data',
                                 dot_path.replace('.', os.sep) + '.csv')
        try:
            os.remove(data_path)
        except:
            pass
        data_path = os.path.join(workspace, 'projects', project, 'tests',
                                 dot_path.replace('.', os.sep) + '.csv')
        try:
            os.remove(data_path)
        except:
            pass

    return errors


def duplicate_element(workspace, project, element_type, original_file_dot_path,
                      new_file_dot_path):
    errors = []
    if element_type == 'test':
        folder = 'tests'
    elif element_type == 'page':
        folder = 'pages'
    elif element_type == 'suite':
        folder = 'suites'
    else:
        errors.append('Element type is incorrect')
    if not errors:
        if original_file_dot_path == new_file_dot_path:
            errors.append('New file cannot be the same as the original')
        else:
            root_path = os.path.join(workspace, 'projects', project)
            original_file_rel_path = original_file_dot_path.replace('.', os.sep) + '.py'
            original_file_full_path = os.path.join(root_path, folder, original_file_rel_path)
            new_file_rel_path = new_file_dot_path.replace('.', os.sep) + '.py'
            new_file_full_path = os.path.join(root_path, folder, new_file_rel_path)
            if os.path.exists(new_file_full_path):
                errors.append('A file with that name already exists')

    if not errors:
        try:
            file_manager.create_directory(path=os.path.dirname(new_file_full_path), add_init=True)
            shutil.copyfile(original_file_full_path, new_file_full_path)
        except:
            errors.append('There was an error creating the new file')

    if not errors and element_type == 'test':
        # TODO deprecate data folder
        try:
            original_data_rel_path = original_file_dot_path.replace('.', os.sep) + '.csv'
            original_data_full_path = os.path.join(root_path, 'data', original_data_rel_path)
            new_data_rel_path = new_file_dot_path.replace('.', os.sep) + '.csv'
            new_data_full_path = os.path.join(root_path, 'data', new_data_rel_path)
            os.makedirs(os.path.dirname(new_data_full_path), exist_ok=True)
            shutil.copyfile(original_data_full_path, new_data_full_path)
        except:
            pass
        try:
            original_data_rel_path = original_file_dot_path.replace('.', os.sep) + '.csv'
            original_data_full_path = os.path.join(root_path, 'tests', original_data_rel_path)
            new_data_rel_path = new_file_dot_path.replace('.', os.sep) + '.csv'
            new_data_full_path = os.path.join(root_path, 'tests', new_data_rel_path)
            file_manager.create_directory(path=os.path.dirname(new_data_full_path), add_init=True)
            shutil.copyfile(original_data_full_path, new_data_full_path)
        except:
            pass

    return errors


def choose_driver_by_precedence(cli_drivers=None, suite_drivers=None,
                                settings_default_driver=None):
    """ Defines which browser(s) to use by order of precedence
    The order is the following:
    1. browsers defined by CLI
    2. browsers defined inside a suite
    3. 'default_driver' setting
    4. chrome
    """
    chosen_drivers = []
    if cli_drivers:
        chosen_drivers = cli_drivers
    elif suite_drivers:
        chosen_drivers = suite_drivers
    elif settings_default_driver:
        chosen_drivers = [settings_default_driver]
    else:
        chosen_drivers = ['chrome']  # default default
    return chosen_drivers


# TODO
def load_json_from_file(filepath, ignore_failure=False, default=None):
    json_data = default
    with open(filepath) as json_file:
        try:
            contents = json_file.read()
            if len(contents.strip()):
                json_data = json.loads(contents)
        except Exception as e:
            msg = 'There was an error parsing file {}'.format(filepath)
            print(msg)
            print(traceback.format_exc())
            if not ignore_failure:
                raise Exception(msg).with_traceback(e.__traceback__)
    return json_data


def validate_python_file_syntax(path):
    error = ''
    source = open(path, 'r').read()
    try:
        compile(source, path, 'exec', optimize=0)
    except:
        error = traceback.format_exc(limit=-1)
    return error


def import_module(path):
    """Import a Python module from a given path
    Note: module_from_spec is new in python 3.5
    TODO unit test
    """
    mod = None
    module_dir, module_file = os.path.split(path)
    module_name, module_ext = os.path.splitext(module_file)
    try:
        spec = importlib.util.spec_from_file_location(module_name, path)
        _mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_mod)
        mod = _mod
    except:
        pass
    if not mod:
        try:
            spec = importlib.util.spec_from_file_location(module_name, path)
            _mod = spec.loader.load_module()
            spec.loader.exec_module(_mod)
            mod = _mod
        except:
            pass
    return mod