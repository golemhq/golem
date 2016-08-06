import csv
import datetime
import importlib
import logging
import os
import sys 

from golem.core import test_execution


#TODO clean
def _generate_dict_from_file_structure(full_path):
    """Generates a dictionary with the preserved structure of a given 
    directory (with its files and subdirectories). 
    Files are stored in tuples, with the first element being the name
    of the file without its extention and the second element 
    the dotted path to the file.

    For example, given the directory:
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

    dir_tree = {}
    start = full_path.rfind(os.sep) + 1

    for path, dirs, files in os.walk(full_path):
        folders = path[start:].split(os.sep)
        # remove __init__.py from list of files
        if '__init__.py' in files: 
            files.remove('__init__.py')
        # remove file extentions
        filenames = [x[:-3] for x in files]
        filename_filepath_duple_list = []
        # remove root_dir form folders
        folders_without_root_dir = [x for x in folders if x != root_dir]
        for f in filenames:
            file_with_dotted_path = '.'.join(folders_without_root_dir + [f])
            filename_filepath_duple_list.append((f, file_with_dotted_path))
        subdir_dict = dict.fromkeys(filename_filepath_duple_list)
        parent = reduce(dict.get, folders[:-1], dir_tree)
        parent[folders[-1]] = subdir_dict
    dir_tree = dir_tree[root_dir]
    return dir_tree


def get_test_data(project, test_case):
    ''''''
    data_dict_list = list()

    # check if CSV file == test case name exists
    parents_joined = os.sep.join(parents)
    data_file_path = os.path.join(
                        'projects', 
                        project, 
                        parents,
                        'data', 
                        test_case + '.csv')
    if os.path.exists(data_file_path):
        with open(data_file_path, 'rb') as csv_file:
            dict_reader = csv.DictReader(csv_file)
            for row in dict_reader:
                data_dict_list.append(row)
    else:
        print 'Warning: No data file found'
    print data_dict_list
    return data_dict_list


def get_projects(workspace):
    projects = list()
    path = os.path.join(workspace, 'projects')
    projects = os.walk(path).next()[1]
    return projects


def get_test_cases(workspace, project):
    path = os.path.join(workspace, 'projects', project, 'test_cases')
    test_cases = _generate_dict_from_file_structure(path)
    return test_cases


def get_page_objects(workspace, project):
    path = os.path.join(workspace, 'projects', project, 'pages')
    page_objects = _generate_dict_from_file_structure(path)
    return page_objects


# TODO
def get_suites(selected_project):
    test_suites = list()

    for (dirpath, dirnames, filenames) in os.walk('projects\\%s\\test_suites' % selected_project):
        test_suites.extend(filenames)
        break
    test_suites.remove('__init__.py')

    for (i, tc) in enumerate(test_suites):
        test_suites[i] = tc[:-3]

    return test_suites


def get_selected_test_case(selected_project, selected_test_case):
    '''retrieves the selected test case of the selected project, returns a list
    of lists, where each list is a test case step, and each sublist element is
    a step component ('page','test_object', 'action', etc) '''

    test_case = list()
    test_case_raw = list()
    t = list()

    #read test_case file
    with file('projects\\%s\\test_cases\\%s.py' % (selected_project, selected_test_case)) as f: #fix use os.path.join
        for line in f:
            t.append(line.strip())
    
    #fix test step format will change

    #get all the steps into a dict
    ###test_case_raw = t[t.index('#steps')+1:t.index('#/steps')]
    
    #parse lines and separate each line into a sub-dict
    # for line in test_case_raw:
    #     #assert lines do not have 4 columns,
    #     if 'assert' in line:
    #         new_line = [line.partition(' ')[0],line.partition(' ')[2],'','']
    #     else:
    #         new_line = [
    #             line.split('.')[0],
    #             line.split('.')[1],
    #             line.split('.')[2].split('(')[0],
    #             line.split('(')[1].replace(')','').replace('"','')] #magic for getting the argument without "" if there is any, * magic *
    #     test_case.append(new_line)

    #return test_case
    return t


def get_suite_test_cases(project, suite):
    ''''''
    tests = list()

    suite_module = importlib.import_module('projects.{0}.test_suites.{1}'.
        format(project, suite), package=None)
    tests = suite_module.test_case_list

    return tests


def get_test_case_class(project_name, test_case_name):
    '''Returns the class of a module of the same name.
    The class name might be a package/module path separated by dots'''

    # TODO verify the file exists before trying to import
    modulex = importlib.import_module(
        'projects.{0}.test_cases.{1}'.format(project_name, test_case_name))
    test_case_class = getattr(modulex, test_case_name)
    return test_case_class


def get_global_settings():
    '''get global settings from root folder'''

    settings = {}
    if os.path.exists('settings.conf'):
        execfile("settings.conf", settings)
        settings.pop("__builtins__", None) # remove __builtins__ key, not used
    else:
        print 'Warning: global Settings file is not present'

    return settings


def get_project_settings(project, global_settings):
    '''get project level settings from selected project folder,
    overrides any global settings'''

    project_settings = {}
    project_settings_path = os.path.join('projects', project, project_settings.conf)
    if os.path.exists(project_settings_path):
        execfile(project_settings_path, project_settings)
        project_settings.pop("__builtins__", None) # remove __builtins__ key, not used
    else:
        print 'Warning: project Settings file is not present'
    # merge global and project settings
    # TODO
    for setting in project_settings:
        if setting in global_settings:
            global_settings[setting] = project_settings[setting]
        else:
            global_settings[setting] = project_settings[setting]

    return global_settings

    
def run_gui():
    from golem import gui

    gui.root_path = test_execution.root_path

    gui.app.run(debug=True, host='0.0.0.0', port=5000)


def get_current_time():
    time_format = "%Y-%m-%d-%H.%M.%S"
    return datetime.datetime.today().strftime(time_format)


def is_test_suite(project, test_case_or_suite):
    suites = get_suites(project)
    if test_case_or_suite in suites:
        return True
    else:
        return False


def display_tree_structure_command_line(structure, lvl=0):
    """Displays a directory tree structure to the command line"""
    for key, value in structure.iteritems():
        if type(key) is tuple:
            print '{}> {}'.format(' '*lvl*4, key[0])
        else:
            print '{}{}/'.format(' '*lvl*4, key)
            display_tree_structure_command_line(value, lvl+1)