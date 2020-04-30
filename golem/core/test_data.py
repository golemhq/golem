"""Methods for dealing with test data files

Data files have csv extensions and are stored in the same
directory as the test.
"""
import csv
import os

from golem.core import utils, session


def save_external_test_data_file(project, full_test_case_name, test_data):
    """Save data to external file (csv).

    full_test_case_name must be a relative dot path
    test_data must be a list of dictionaries
    """
    tc_name, parents = utils.separate_file_from_parents(full_test_case_name)
    data_path_tests_folder = os.path.join(session.testdir, 'projects', project,
                                          'tests', os.sep.join(parents))
    data_file_path = os.path.join(data_path_tests_folder, '{}.csv'.format(tc_name))
    if os.path.isfile(data_file_path) or test_data:
        # update data file only if it already exists or there's data
        with open(data_file_path, 'w', encoding='utf-8') as data_file:
            if test_data:
                writer = csv.DictWriter(data_file, fieldnames=test_data[0].keys(),
                                        lineterminator='\n')
                writer.writeheader()
                for row in test_data:
                    writer.writerow(row)
            else:
                data_file.write('')


def get_external_test_data(project, full_test_case_name):
    """Get data from file (csv)."""
    data_list = []
    test, parents = utils.separate_file_from_parents(full_test_case_name)
    data_file_path = os.path.join(session.testdir, 'projects', project, 'tests',
                                  os.sep.join(parents), '{}.csv'.format(test))
    if os.path.isfile(data_file_path):
        with open(data_file_path, 'r', encoding='utf-8') as csv_file:
            dict_reader = csv.DictReader(csv_file)
            for data_set in dict_reader:
                data_list.append(dict(data_set))
    return data_list


def get_internal_test_data(project, full_test_case_name, repr_strings=False):
    """Get test data defined inside the test itself."""
    # check if test has data variable defined
    data_list = []
    tc_name, parents = utils.separate_file_from_parents(full_test_case_name)
    path = os.path.join(session.testdir, 'projects', project, 'tests',
                        os.sep.join(parents), '{}.py'.format(tc_name))
    test_module, _ = utils.import_module(path)

    if hasattr(test_module, 'data'):
        msg_not_list_not_dict = ('Warning: infile test data must be a dictionary '
                                 'or a list of dictionaries\nCurrent value is:\n{}\n')
        data_variable = getattr(test_module, 'data')
        if type(data_variable) == dict:
            data_list.append(data_variable)
        elif type(data_variable) == list:
            if all(isinstance(item, dict) for item in data_variable):
                data_list = data_variable
            else:
                print(msg_not_list_not_dict.format(data_variable))
        else:
            print(msg_not_list_not_dict.format(data_variable))
    if repr_strings:
        # replace string values for their repr values
        data_list_clean = []
        for data_dict in data_list:
            d = {}
            for k, v in data_dict.items():
                if type(v) == str:
                    d[k] = repr(v)
                else:
                    d[k] = v
            data_list_clean.append(d)
        data_list = data_list_clean
    return data_list


def get_test_data(project, full_test_case_name, repr_strings=False):
    """Get test data.

    The order of priority is:
    1. data defined in a csv file same name and folder as the test
    2. data defined in the test itself as a list of dictionaries

    Returns a list of dictionaries"""
    data_list = []
    external_data = get_external_test_data(project, full_test_case_name)
    if external_data:
        data_list = external_data
    else:
        internal_data = get_internal_test_data(project, full_test_case_name,
                                               repr_strings=repr_strings)
        if internal_data:
            data_list = internal_data
    if not data_list:
        data_list.append({})
    return data_list


def remove_csv_if_exists(project, full_test_case_name):
    """Remove csv data file from tests/ folder"""
    tc_name, parents = utils.separate_file_from_parents(full_test_case_name)
    data_file_path_tests_folder = os.path.join(session.testdir, 'projects', project,
                                               'tests', os.sep.join(parents),
                                               '{}.csv'.format(tc_name))
    if os.path.isfile(data_file_path_tests_folder):
        os.remove(data_file_path_tests_folder)
