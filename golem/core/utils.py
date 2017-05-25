import csv
import datetime
import imp
import importlib
import shutil
import json
import os
import uuid

from functools import reduce
from collections import OrderedDict

import golem


def _generate_dict_from_file_structure(full_path):
    """Generates a dictionary with the preserved structure of a given
    directory (with its files and subdirectories).
    Files are stored in tuples, with the first element being the name
    of the file without its extention and the second element
    the dotted path to the file.

    For example, given the following directory:
    test/
         subdir1/
                 subdir2/
                         file5
                 file3
                 file4

         file1
         file2

    The result will be:
    test = {
        'subdir1': {
            'subdir2': {
                'subdir2': {
                    ('file5', 'subdir1.subdir2.file5'): None,
                },
                ('file3', 'subdir1.file3'): None,
                ('file4', 'subdir1.file4'): None,
        },
        ('file1', 'file1'): None,
        ('file2', 'file2'): None,
    }
    """
    root_dir = os.path.basename(os.path.normpath(full_path))

    dir_tree = OrderedDict()
    start = full_path.rfind(os.sep) + 1

    for path, dirs, files in os.walk(full_path):
        folders = path[start:].split(os.sep)
        # remove __init__.py from list of files
        if '__init__.py' in files:
            files.remove('__init__.py')
        # mac OS creates '.DS_store' files
        if '.DS_Store' in files:
            files.remove('.DS_Store')
        # remove files that are not .py extension and remove extensions
        filenames = [x[:-3] for x in files if x.split('.')[1] == 'py']
        filename_filepath_duple_list = []
        # remove root_dir form folders
        folders_without_root_dir = [x for x in folders if x != root_dir]
        for f in filenames:
            file_with_dotted_path = '.'.join(folders_without_root_dir + [f])
            filename_filepath_duple_list.append((f, file_with_dotted_path))
        subdir_dict = OrderedDict.fromkeys(filename_filepath_duple_list)
        parent = reduce(OrderedDict.get, folders[:-1], dir_tree)
        parent.update({folders[-1]: subdir_dict})
        parent.move_to_end(folders[-1], last=False)
    dir_tree = dir_tree[root_dir]
    return dir_tree


def get_test_cases(workspace, project):
    path = os.path.join(workspace, 'projects', project, 'test_cases')
    test_cases = _generate_dict_from_file_structure(path)
    return test_cases


def get_page_objects(workspace, project):
    path = os.path.join(workspace, 'projects', project, 'pages')
    page_objects = _generate_dict_from_file_structure(path)
    return page_objects


def get_suites(workspace, project):
    path = os.path.join(workspace, 'projects', project, 'test_suites')
    
    ## suites = _generate_dict_from_file_structure(path)

    suites = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

    if '__init__.py' in suites:
        suites.remove('__init__.py')
    # remove files that are not .py extension and remove extensions
    suites = [x[:-3] for x in suites if x.split('.')[1] == 'py']
    return suites


def get_projects(workspace):
    projects = []
    path = os.path.join(workspace, 'projects')
    projects = os.walk(path).__next__()[1]
    return projects


def get_files_in_directory_dotted_path(base_path):
    '''generate a list of all the files inside a directory and
    subdirectories with the relative path as a dotted string.
    example:
    given C:/base_dir/dir/sub_dir/file.py
    get_files_in_directory_dotted_path('C:/base_dir/'):
    >['dir.sub_dir.file']'''
    all_files = []
    files_with_dotted_path = []
    for path, subdirs, files in os.walk(base_path):
        for name in files:
            if name not in ['__init__.py', '.DS_Store']:
                filepath = os.path.join(path, os.path.splitext(name)[0])
                all_files.append(filepath)
    for file in all_files:
        rel_path_as_list = file.replace(base_path, '').split(os.sep)
        rel_path_as_list = [x for x in rel_path_as_list if x != '']
        files_with_dotted_path.append('.'.join(rel_path_as_list))
    return files_with_dotted_path


def get_test_data(workspace, project, full_test_case_name):
    '''Test cases can have multiple sets of data
    This method generates a dict for each set and returns
    a list of dicts'''
    data_dict_list = []

    # check if CSV file == test case name exists
    test, parents = separate_file_from_parents(full_test_case_name)
    data_file_path = os.path.join(workspace, 'projects', project,
                                  'data', os.sep.join(parents),
                                  '{}.csv'.format(test))
    if not os.path.exists(data_file_path):
        print('Warning: No data file found for {}'.format(full_test_case_name))
    else:
        with open(data_file_path, 'r', encoding='utf8') as csv_file:
            dict_reader = csv.DictReader(csv_file)
            for data_set in dict_reader:
                data_dict_list.append(data_set)

    if not data_dict_list:
        data_dict_list = []
    return data_dict_list


def get_suite_test_cases(project, suite):
    '''Return a list with all the test cases of a given suite'''
    tests = list()

    suite_module = importlib.import_module('projects.{0}.test_suites.{1}'
                                           .format(project, suite),
                                           package=None)
    tests = suite_module.test_case_list

    return tests


def get_directory_suite_test_cases(workspace, project, suite):
    '''Return a list with all the test cases of a given directory suite
    a directory suite is a directory inside "/test_cases" folder'''
    tests = list()

    path = os.path.join(workspace, 'projects', project, 'test_cases', suite)
    tests = get_files_in_directory_dotted_path(path)
    tests = ['.'.join((suite, x)) for x in tests]

    return tests


def get_suite_amount_of_workers(workspace, project, suite):
    amount = 1

    suite_module = importlib.import_module('projects.{0}.test_suites.{1}'.format(project, suite),
                                           package=None)
    if hasattr(suite_module, 'workers'):
        amount = suite_module.workers

    return amount


def get_suite_browsers(workspace, project, suite):
    browsers = []
    suite_module = importlib.import_module('projects.{0}.test_suites.{1}'.format(project, suite),
                                           package=None)
    if hasattr(suite_module, 'browsers'):
        browsers = suite_module.browsers

    return browsers


# def get_test_case_class(project_name, test_case_name):
#     '''Returns the class present in a module of the same name.
#     'test_case_name' might be the full path to the module,
#     separeted by dots'''

#     # TODO verify the file exists before trying to import
#     modulex = importlib.import_module('projects.{0}.test_cases.{1}'
#                                       .format(project_name, test_case_name))
#     test_case_only = test_case_name.split('.')[-1]
#     test_case_class = getattr(modulex, test_case_only)
#     return test_case_class

def assign_settings_default_values(settings):
    if not 'screenshot_on_step' in settings:
        settings['screenshot_on_step'] = False
    return settings


def get_global_settings():
    '''get global settings from root folder'''

    settings = {}
    if os.path.exists('settings.conf'):
        ## execfile("settings.conf", settings)

        # the following code parses a conf file in python 3.x
        with open("settings.conf") as f:
            code = compile(f.read(), "settings.conf", 'exec')
            exec(code, settings)
            settings.pop("__builtins__", None)
    else:
        print('Warning: global Settings file is not present')

    settings = assign_settings_default_values(settings)

    return settings


def get_project_settings(project, global_settings):
    '''get project level settings from selected project folder,
    this overrides any global settings'''

    project_settings = {}
    project_settings_path = os.path.join('projects',
                                         project,
                                         'settings.conf')
    if os.path.exists(project_settings_path):
        ## execfile(project_settings_path, project_settings)

        # the following code parses a conf file in python 3.x
        with open(project_settings_path) as f:
            code = compile(f.read(), project_settings_path, 'exec')
            exec(code, project_settings)
            project_settings.pop("__builtins__", None)
    else:
        print('Warning: project Settings file is not present')
    # merge global and project settings
    for setting in project_settings:
        if setting in global_settings:
            global_settings[setting] = project_settings[setting]
        else:
            global_settings[setting] = project_settings[setting]

    return global_settings


def get_timestamp():
    time_format = "%Y.%m.%d.%H.%M.%S.%f"
    timestamp = datetime.datetime.today().strftime(time_format)
    # remove last 3 decimal places from microseconds
    timestamp = timestamp[:-3]
    return timestamp


def test_case_exists(workspace, project, full_test_case_name):
    test, parents = separate_file_from_parents(full_test_case_name)
    path = os.path.join(workspace,
                        'projects',
                        project,
                        'test_cases',
                        os.sep.join(parents),
                        '{}.py'.format(test))
    test_exists = os.path.isfile(path)
    return test_exists


def test_suite_exists(workspace, project, full_test_suite_name):
    suite, parents = separate_file_from_parents(full_test_suite_name)
    path = os.path.join(workspace,
                        'projects',
                        project,
                        'test_suites',
                        os.sep.join(parents),
                        '{}.py'.format(suite))
    suite_exists = os.path.isfile(path)
    return suite_exists


def display_tree_structure_command_line(structure, lvl=0):
    """Displays a directory tree structure to the command line"""
    for key, value in structure.items():
        if type(key) is tuple:
            print('{}> {}'.format(' ' * lvl * 4, key[0]))
        else:
            print('{}{}/'.format(' ' * lvl * 4, key))
            display_tree_structure_command_line(value, lvl + 1)


def separate_file_from_parents(full_filename):
    """Receives a full filename with parents (separated by dots)
    Returns a duple, first element is the filename and second element
    is the list of parents that might be empty"""
    splitted = full_filename.split('.')
    file = splitted.pop()
    parents = splitted
    return (file, parents)


def is_first_level_directory(workspace, project, directory):
    path = os.path.join(workspace,
                        'projects',
                        project,
                        'test_cases',
                        directory)
    return os.path.isdir(path)


def generate_page_object_module(project, parent_module,
                                full_path, page_path_list):
    if len(page_path_list) > 1:
        if not hasattr(parent_module, page_path_list[0]):
            new_module = imp.new_module(page_path_list[0])
            setattr(parent_module,
                    page_path_list[0],
                    new_module)
        else:
            new_module = getattr(parent_module, page_path_list[0])
        page_path_list.pop(0)
        new_module = generate_page_object_module(project, new_module,
                                                 full_path, page_path_list)
        setattr(parent_module, page_path_list[0], new_module)
    else:
        imported_module = importlib.import_module('projects.{}.pages.{}'
                                                  .format(project, full_path))
        setattr(parent_module, page_path_list[0], imported_module)
    return parent_module


def create_new_directory(path_list=None, path=None, add_init=False):
    if path_list:
        path = os.sep.join(path_list)
    if not os.path.exists(path):
        os.makedirs(path)
    if add_init:
        # add __init__.py file to make the new directory a python package
        init_path = os.path.join(path, '__init__.py')
        open(init_path, 'a').close()


def create_new_project(workspace, project):
    create_new_directory(path_list=[workspace, 'projects', project], add_init=True)
    create_new_directory(path_list=[workspace, 'projects', project, 'data'], add_init=False)
    create_new_directory(path_list=[workspace, 'projects', project, 'pages'], add_init=True)
    create_new_directory(path_list=[workspace, 'projects', project, 'reports'], add_init=False)
    create_new_directory(path_list=[workspace, 'projects', project, 'test_cases'], add_init=True)
    create_new_directory(path_list=[workspace, 'projects', project, 'test_suites'], add_init=True)
    extend_path = os.path.join(workspace, 'projects', project, 'extend.py')
    open(extend_path, 'a').close()
    settings_path = os.path.join(workspace, 'projects', project, 'settings.conf')
    open(settings_path, 'a').close()


def create_demo_project(workspace):
    create_new_directory(path_list=[workspace, 'projects', 'demo'])
    source = os.path.join(golem.__path__[0], 'templates/demo_project')
    destination = os.path.join(workspace, 'projects', 'demo')
    shutil.copytree(source, destination)


def create_test_dir(workspace):
    create_new_directory(path_list=[workspace], add_init=True)
    create_new_directory(path_list=[workspace, 'projects'], add_init=True)
    create_new_directory(path_list=[workspace, 'drivers'], add_init=False)
    
    golem_py_content = ("import os\n"
                        "import sys\n"
                        "\n\n"
                        "# deactivate .pyc extention file generation\n"
                        "sys.dont_write_bytecode = True\n"
                        "\n\n"
                        "if __name__ == '__main__':\n"
                        "    del sys.path[0]\n"
                        "    sys.path.append('')\n\n"
                        "    from golem.main import execute_from_command_line\n\n"
                        "    execute_from_command_line(os.getcwd())\n")
    golem_py_path = os.path.join(workspace, 'golem.py')
    with open(golem_py_path, 'a') as golem_py_file:
        golem_py_file.write(golem_py_content)

    settings_content = ("\nimplicit_wait = 10\n"
                        "screenshot_on_error = True\n"
                        "wait_hook = None\n")
    settings_path = os.path.join(workspace, 'settings.conf')
    with open(settings_path, 'a') as settings_file:
        settings_file.write(settings_content)

    users_content = [
        {
            "id": "000000001",
            "username": "admin",
            "password": "admin",
            "is_admin": True,
            "projects": ["*"]
        }
    ]
    users_path = os.path.join(workspace, 'users.json')
    open(users_path, 'a').close()
    create_user(workspace, 'admin', 'admin', True, ["*"], ["*"])


def create_user(workspace, username, password, is_admin, projects, reports):
    errors = []
    new_user = {

    }

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


