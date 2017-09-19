import csv
import os

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
            new_file = open(data_file_path, 'w+').close()
        with open(data_file_path, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=test_data[0].keys(), lineterminator='\n')
            writer.writeheader()
            for row in test_data:
                writer.writerow(row)


def is_data_variable(root_path, project, parents, test_case_name, parameter_name):
    full_path = parents + [test_case_name]
    test_data = utils.get_test_data_dict_list(root_path, project, '.'.join(full_path))
    print('TEST DATA IN IS DATA VARIABLE', test_data)
    if test_data:
        if parameter_name in test_data[0].keys():
            return True
    return False
