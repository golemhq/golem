import csv
import os

from golem.core import utils


# def get_data(content):
#     key_value_pairs = {}

#     for line in content:
#         if '=' in line:
#             key = line.split('=')[0].strip()
#             value = line.split('=')[1].strip().replace('\'','').replace('\"', '')
#             key_value_pairs[key] = value
#     return key_value_pairs


# def parse_test_data(root_path, project, parents, test_case_name):

#     parents_joined = os.sep.join(parents)

#     path = os.path.join(
#                 root_path, 
#                 'projects', 
#                 project, 
#                 'data', 
#                 parents_joined, 
#                 test_case_name + '.py')

#     with open(path) as f:
#         content = f.readlines()

#     key_value_pairs = get_data(content)

#     return key_value_pairs


def save_test_data(root_path, project, full_test_case_name, test_data):
    if test_data[0]:
        tc_name, parents = utils.separate_file_from_parents(full_test_case_name)
        data_path = os.path.join(root_path,
                                 'projects',
                                 project,
                                 'data',
                                 os.sep.join(parents),
                                 '{}.csv'.format(tc_name))
        with open(data_path, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=test_data[0].keys(), lineterminator='\n')
            writer.writeheader()
            for row in test_data:
                writer.writerow(row)


def is_data_variable(root_path, project, parents, test_case_name, parameter_name):
    parents += [test_case_name]
    test_data = utils.get_test_data(root_path, project, '.'.join(parents))
    if parameter_name in test_data[0].keys():
        return True
    else: 
        return False
