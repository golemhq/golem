import csv
import imp
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


# def _generate_dict_from_file_structure(full_path):
#     """Generates a dictionary with the preserved structure of a given
#     directory (with its files and subdirectories).
#     Files are stored in tuples, with the first element being the name
#     of the file without its extention and the second element
#     the dotted path to the file.

#     For example, given the following directory:
#     test/
#          subdir1/
#                  subdir2/
#                          file5
#                  file3
#                  file4

#          file1
#          file2

#     The result will be:
#     test = {
#         'subdir1': {
#             'subdir2': {
#                 'subdir2': {
#                     ('file5', 'subdir1.subdir2.file5'): None,
#                 },
#                 ('file3', 'subdir1.file3'): None,
#                 ('file4', 'subdir1.file4'): None,
#         },
#         ('file1', 'file1'): None,
#         ('file2', 'file2'): None,
#     }
#     """
#     root_dir = os.path.basename(os.path.normpath(full_path))

#     dir_tree = OrderedDict()
#     start = full_path.rfind(os.sep) + 1

#     for path, dirs, files in os.walk(full_path):
#         folders = path[start:].split(os.sep)
#         # remove __init__.py from list of files
#         if '__init__.py' in files:
#             files.remove('__init__.py')
#         # mac OS creates '.DS_store' files
#         if '.DS_Store' in files:
#             files.remove('.DS_Store')
#         # remove files that are not .py extension and remove extensions
#         filenames = [x[:-3] for x in files if x.split('.')[1] == 'py']
#         filename_filepath_duple_list = []
#         # remove root_dir form folders
#         folders_without_root_dir = [x for x in folders if x != root_dir]
#         for f in filenames:
#             file_with_dotted_path = '.'.join(folders_without_root_dir + [f])
#             filename_filepath_duple_list.append((f, file_with_dotted_path))
#         subdir_dict = OrderedDict.fromkeys(filename_filepath_duple_list)
#         parent = reduce(OrderedDict.get, folders[:-1], dir_tree)
#         parent.update({folders[-1]: subdir_dict})

#         # this code is added to give support to python 2.7
#         # support for python 2.7 has been dropped
#         # which does not have move_to_end method
#         # if not hasattr(OrderedDict, 'move_to_end'):
#         #     def move_to_end(self, key, last=True):
#         #         link_prev, link_next, key = link = self._OrderedDict__map[key]
#         #         link_prev[1] = link_next
#         #         link_next[0] = link_prev
#         #         root = self._OrderedDict__root
#         #         if last:
#         #             last = root[0]
#         #             link[0] = last
#         #             link[1] = root
#         #             last[1] = root[0] = link
#         #     OrderedDict.move_to_end = move_to_end
#         # end of python 2.7 support code

#         parent.move_to_end(folders[-1], last=False)
#     dir_tree = dir_tree[root_dir]
#     return dir_tree


def _directory_element(elem_type, name, dot_path=None):
    element = {
        'type': elem_type,
        'name': name,
        'dot_path': dot_path,
        'sub_elements': []
    }
    return element


def _generate_dict_from_file_structure(full_path, original_path=None):
    root_dir_name = os.path.basename(os.path.normpath(full_path))
    if not original_path:
        original_path = full_path
    _ = os.path.relpath(full_path, original_path).replace(os.sep, '.')
    element = _directory_element('directory', root_dir_name, _)

    all_sub_elements = os.listdir(full_path)
    files = []
    directories = []
    for elem in all_sub_elements: 
        if os.path.isdir(os.path.join(full_path, elem)):
            if elem not in ['__pycache__']:
                directories.append(elem)
        else:
            cond1 = elem not in ['__init__.py', '.DS_Store']
            cond2 = not elem.endswith('.csv')
            if cond1 and cond2:
                files.append(os.path.splitext(elem)[0])
    for directory in directories:
        _ = _generate_dict_from_file_structure(os.path.join(full_path, directory),
                                               original_path)
        element['sub_elements'].append(_)
    for filename in files:
        full_file_path = os.path.join(full_path, filename)

        rel_file_path = os.path.relpath(full_file_path, original_path)
        dot_file_path = rel_file_path.replace(os.sep, '.')
        file_element = _directory_element('file', filename, dot_file_path)
        element['sub_elements'].append(file_element)

    return element


def get_test_cases(workspace, project):
    path = os.path.join(workspace, 'projects', project, 'tests')
    test_cases = _generate_dict_from_file_structure(path)
    return test_cases


def get_pages(workspace, project):
    path = os.path.join(workspace, 'projects', project, 'pages')
    pages = _generate_dict_from_file_structure(path)
    return pages


def get_suites(workspace, project):
    path = os.path.join(workspace, 'projects', project, 'suites')
    suites = _generate_dict_from_file_structure(path)
    return suites


def get_projects(workspace):
    projects = []
    path = os.path.join(workspace, 'projects')
    projects = next(os.walk(path))[1]
    return projects


def project_exists(workspace, project):
    return project in get_projects(workspace)


def get_files_in_directory_dot_path(base_path):
    '''
    generate a list of all the files inside a directory and
    subdirectories with the relative path as a dotted string.
    for example, given:
    C:/base_dir/dir/sub_dir/file.py
    get_files_in_directory_dotted_path('C:/base_dir/'):
    >['dir.sub_dir.file']
    '''
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


def get_suite_module(workspace, project, suite):
    module_name = 'projects.{0}.suites.{1}'.format(project, suite)
    suite_module = importlib.import_module(module_name, package=None)
    return suite_module


def get_suite_test_cases(workspace, project, suite):
    '''Return a list with all the test cases of a given suite'''
    tests = []
    module_name = 'projects.{0}.suites.{1}'.format(project, suite)
    suite_module = importlib.import_module(module_name, package=None)
    if '*' in suite_module.tests:
        path = os.path.join(workspace, 'projects', project, 'tests')
        tests = get_files_in_directory_dot_path(path)
    else:
        for test in suite_module.tests:
            if test[-1] == '*':
                this_dir = os.path.join(test[:-2])
                path = os.path.join(workspace, 'projects', project,
                                    'tests', this_dir)
                this_dir_tests = get_files_in_directory_dot_path(path)
                this_dir_tests = ['{}.{}'.format(this_dir, x) for x in this_dir_tests]
                tests = tests + this_dir_tests
            else:
                tests.append(test)
    return tests


def get_directory_suite_test_cases(workspace, project, suite):
    '''Return a list with all the test cases of a given directory suite
    a directory suite is a directory inside "/test_cases" folder'''
    tests = list()

    path = os.path.join(workspace, 'projects', project, 'tests', suite)
    tests = get_files_in_directory_dot_path(path)
    tests = ['.'.join((suite, x)) for x in tests]

    return tests


def get_suite_amount_of_workers(workspace, project, suite):
    amount = 1
    suite_module = importlib.import_module('projects.{0}.suites.{1}'.format(project, suite),
                                           package=None)
    if hasattr(suite_module, 'workers'):
        amount = suite_module.workers

    return amount


def get_suite_browsers(workspace, project, suite):
    browsers = []
    module_name = 'projects.{0}.suites.{1}'.format(project, suite)
    suite_module = importlib.import_module(module_name, package=None)
    if hasattr(suite_module, 'browsers'):
        browsers = suite_module.browsers

    return browsers


def get_suite_environments(workspace, project, suite):
    environments = []
    module_name = 'projects.{0}.suites.{1}'.format(project, suite)
    suite_module = importlib.import_module(module_name, package=None)
    if hasattr(suite_module, 'environments'):
        environments = suite_module.environments

    return environments


def get_timestamp():
    time_format = "%Y.%m.%d.%H.%M.%S.%f"
    timestamp = datetime.today().strftime(time_format)
    # remove last 3 decimal places from microseconds
    timestamp = timestamp[:-3]
    return timestamp


def get_date_from_timestamp(timestamp):
    date = datetime.strptime(timestamp, '%Y.%m.%d.%H.%M.%S.%f')
    return date


def test_case_exists(workspace, project, full_test_case_name):
    test, parents = separate_file_from_parents(full_test_case_name)
    path = os.path.join(workspace, 'projects', project, 'tests',
                        os.sep.join(parents), '{}.py'.format(test))
    test_exists = os.path.isfile(path)
    return test_exists


def test_suite_exists(workspace, project, full_test_suite_name):
    suite, parents = separate_file_from_parents(full_test_suite_name)
    path = os.path.join(workspace, 'projects', project, 'suites',
                        os.sep.join(parents), '{}.py'.format(suite))
    suite_exists = os.path.isfile(path)
    return suite_exists


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


def generate_page_object_module(project, parent_module, full_path, page_path_list):
    if len(page_path_list) > 1:
        if not hasattr(parent_module, page_path_list[0]):
            new_module = imp.new_module(page_path_list[0])
            setattr(parent_module, page_path_list[0], new_module)
        else:
            new_module = getattr(parent_module, page_path_list[0])
        page_path_list.pop(0)
        new_module = generate_page_object_module(project, new_module, full_path, page_path_list)
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


def create_new_directories(root_path, directories, add_init=False):
    path = root_path
    for directory in directories:
        path = os.path.join(path, directory)
        create_new_directory(path=path, add_init=add_init)


def create_new_project(workspace, project):
    create_new_directory(path_list=[workspace, 'projects', project], add_init=True)
    create_new_directory(path_list=[workspace, 'projects', project, 'data'], add_init=False)
    create_new_directory(path_list=[workspace, 'projects', project, 'pages'], add_init=True)
    create_new_directory(path_list=[workspace, 'projects', project, 'reports'], add_init=False)
    create_new_directory(path_list=[workspace, 'projects', project, 'tests'], add_init=True)
    create_new_directory(path_list=[workspace, 'projects', project, 'suites'], add_init=True)
    extend_path = os.path.join(workspace, 'projects', project, 'extend.py')
    open(extend_path, 'a').close()

    settings_path = os.path.join(workspace, 'projects', project, 'settings.json')
    with open(settings_path, 'a') as settings_file:
        settings_file.write(settings_manager.REDUCED_SETTINGS_FILE_CONTENT)

    environments_path = os.path.join(workspace, 'projects', project, 'environments.json')
    with open(environments_path, 'a') as environments_file:
        environments_file.write('{}')
    print('Project {} created'.format(project))


def create_demo_project(workspace):
    create_new_directory(path_list=[workspace, 'projects', 'demo'])
    source = os.path.join(golem.__path__[0], 'templates/demo_project')
    destination = os.path.join(workspace, 'projects', 'demo')
    shutil.copytree(source, destination)


def create_test_dir(workspace):
    create_new_directory(path_list=[workspace], add_init=True)
    create_new_directory(path_list=[workspace, 'projects'], add_init=True)
    create_new_directory(path_list=[workspace, 'drivers'], add_init=False)

    # copy drivers from golem/bin/drivers to test_dir/drivers
    pkgdir = sys.modules['golem'].__path__[0]
    #sourcepath = os.path.join(pkgdir, 'bin', 'drivers')
    #destination_path = os.path.join(workspace, 'drivers')
    #shutil.copytree(sourcepath, destination_path)

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

    settings_path = os.path.join(workspace, 'settings.json')
    with open(settings_path, 'a') as settings_file:
        settings_file.write(settings_manager.SETTINGS_FILE_CONTENT)

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


def code_syntax_is_valid(code):
    error = ''
    try:
        compile(code, '<string>', 'exec')
    except Exception as e:
        error = 'syntax error'
    return error


def delete_element(workspace, project, element_type, full_path):
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
                        full_path.replace('.', os.sep) + '.py')
    if not os.path.exists(path):
        errors.append('File {} does not exist'.format(full_path))
    else:
        try:
            os.remove(path)
        except:
            errors.append('There was an error removing file {}'.format(full_path))

    if element_type == 'test':
        data_path = os.path.join(workspace, 'projects', project, 'data',
                                 full_path.replace('.', os.sep) + '.csv')
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
            shutil.copyfile(original_file_full_path, new_file_full_path)
        except:
            errors.append('There was an error creating the new file')

    if not errors and element_type == 'test':
        try:
            original_data_rel_path = original_file_dot_path.replace('.', os.sep) + '.csv'
            original_data_full_path = os.path.join(root_path, 'data', original_data_rel_path)
            new_data_rel_path = new_file_dot_path.replace('.', os.sep) + '.csv'
            new_data_full_path = os.path.join(root_path, 'data', new_data_rel_path)
            shutil.copyfile(original_data_full_path, new_data_full_path)
        except:
            pass

    return errors


def choose_driver_by_precedence(cli_drivers=None, suite_drivers=None,
                                settings_default_driver=None):
    chosen_drivers = []
    if cli_drivers:
        chosen_drivers = cli_drivers
    elif suite_drivers:
        chosen_drivers = suite_drivers
    elif settings_default_driver:
        chosen_drivers = [settings_default_driver]
    else:
        chosen_drivers = ['chrome']  # hardcoded default
    return chosen_drivers


def load_json_from_file(filepath):
    json_data = None
    with open(filepath) as json_file:
        try:
            json_data = json.load(json_file)
        except Exception as e:
            msg = 'There was an error parsing file {}'.format(filepath)
            print(traceback.format_exc())
            raise Exception(msg).with_traceback(e.__traceback__)
    return json_data
