import csv
import os
import sys
import importlib

from golem.core import utils


def save_test_data(root_path, project, full_test_case_name, test_data):
    if test_data[0]:
        tc_name, parents = utils.separate_file_from_parents(full_test_case_name)
        data_directory_path = os.path.join(root_path, 'projects', project, 'data',
                                           os.sep.join(parents))
        data_file_path = os.path.join(data_directory_path, '{}.csv'.format(tc_name))
        # if the data file does not exist, create it
        if not os.path.exists(data_directory_path):
            os.makedirs(data_directory_path)
        if not os.path.isfile(data_file_path):
            open(data_file_path, 'w+').close()
        with open(data_file_path, 'w') as data_file:
            writer = csv.DictWriter(data_file, fieldnames=test_data[0].keys(), lineterminator='\n')
            writer.writeheader()
            for row in test_data:
                writer.writerow(row)


def get_test_data(workspace, project, full_test_case_name):
    """get test data. The order of priority is:
    1. data defined in a csv file in /data/ folder,
    same directory structure as the test. Soon to be deprecated. # TODO
    2. data defined in a csv file in /tests/ folder, same folder as the test
    3. data defined in the test itself
    Try to convert each value to a Python var type. Fall back to string.
    Returns a list of dictionaries"""
    data_list = []

    test, parents = utils.separate_file_from_parents(full_test_case_name)
    data_file_path_data_folder = os.path.join(workspace, 'projects', project,
                                              'data', os.sep.join(parents),
                                              '{}.csv'.format(test))
    data_file_path_test_folder = os.path.join(workspace, 'projects', project,
                                              'tests', os.sep.join(parents),
                                              '{}.csv'.format(test))
    # check if csv file exists in /data/ folder
    if os.path.exists(data_file_path_data_folder):
        with open(data_file_path_data_folder, 'r', encoding='utf8') as csv_file:
            dict_reader = csv.DictReader(csv_file)
            for data_set in dict_reader:
                d = {}
                for item in data_set.items():
                    try:
                        d[item[0]] = literal_eval(item[1])
                    except:
                        d[item[0]] = item[1]
                data_list.append(d)
        print(('Warning: data files defined in the /data/ folder will soon '
               'be deprecated. Test data files should be placed in the same folder '
               'as the test file.'))               
    # check if csv file exists in /tests/ folder
    elif os.path.exists(data_file_path_test_folder):
        with open(data_file_path_test_folder, 'r', encoding='utf8') as csv_file:
            dict_reader = csv.DictReader(csv_file)
            for data_set in dict_reader:
                d = {}
                for item in data_set.items():
                    try:
                        d[item[0]] = literal_eval(item[1])
                    except:
                        d[item[0]] = item[1]
                data_list.append(d)
    # check if test has data variable defined
    else:
        sys.path.append(os.path.join(workspace, 'projects', project))
        test_module = importlib.import_module('projects.{0}.tests.{1}'
                                              .format(project, full_test_case_name))
        if hasattr(test_module, 'data'):
            data_variable = getattr(test_module, 'data')
            print(data_variable)
            if type(data_variable) == dict:
                data_list.append(data_variable)
            elif type(data_variable) == list:
                if all(isinstance(item, dict) for item in data_variable):
                    data_list = data_variable
                else:
                    print(('Warning: infile test data must be a dictionary or '
                           'a list of dictionaries\n'
                           'Current value is:\n'
                           '{}\n'
                           'Test data for test {} will be ignored'
                           .format(data_variable, full_test_case_name)))
            else: 
                print(('Warning: infile test data must be a dictionary or '
                       'a list of dictionaries\n'
                       'Current value is:\n'
                       '{}\n'
                       'Test data for test {} will be ignored'
                        .format(data_variable, full_test_case_name)))

    if not data_list:
        data_list.append({})

    return data_list


# def get_test_data_dict_list(workspace, project, full_test_case_name):
#     data_dict_list = []
#     data_list = get_test_data(workspace, project, full_test_case_name)
#     for data in data_list:
#         data_dict_list.append(data)
#     return data_dict_list
