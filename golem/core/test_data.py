"""Methods for dealing with test data files

Data files have csv or json extensions and are stored in the same
directory as the test.
"""
import ast
import csv
import json
import os
import traceback

from golem.core import test as test_module
from golem.core import utils


def csv_file_path(project, test_name):
    test = test_module.Test(project, test_name)
    return os.path.join(test.dirname, f'{test.stem_name}.csv')


def save_csv_test_data(project, test_name, test_data):
    """Save data to csv file.
    test_data must be a list of dictionaries
    """
    if test_data:
        with open(csv_file_path(project, test_name), 'w', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=test_data[0].keys(), lineterminator='\n')
            writer.writeheader()
            for row in test_data:
                writer.writerow(row)
    else:
        remove_csv_if_present(project, test_name)


def get_csv_test_data(project, test_name):
    """Get data from csv file as a list of dicts"""
    data_list = []
    csv_path = csv_file_path(project, test_name)
    if os.path.isfile(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            dict_reader = csv.DictReader(f)
            for data_set in dict_reader:
                data_list.append(dict(data_set))
    return data_list


def remove_csv_if_present(project, test_name):
    """Remove csv data file from tests/ folder"""
    csv_path = csv_file_path(project, test_name)
    if os.path.isfile(csv_path):
        os.remove(csv_path)


def json_file_path(project, test_name):
    test = test_module.Test(project, test_name)
    return os.path.join(test.dirname, f'{test.stem_name}.json')


def save_json_test_data(project, test_name, json_data_str):
    """Save data to json file. Data is not saved if json is not valid."""
    if json_data_str and not utils.json_parse_error(json_data_str):
        with open(json_file_path(project, test_name), 'w', encoding='utf-8') as f:
            f.write(json_data_str)


def get_json_test_data(project, test_name):
    """Get data from json file.
    If json data is not of type dict or list of dicts it is ignored.
    """
    json_data = None
    json_path = json_file_path(project, test_name)
    if os.path.isfile(json_path):
        try:
            with open(json_path, encoding='utf-8') as f:
                json_data = json.load(f)
        except json.JSONDecodeError:
            pass
    if type(json_data) is dict:
        return [json_data]
    if type(json_data) is list:
        if all(type(x) is dict for x in json_data):
            return json_data
    return []


def get_json_test_data_as_string(project, test_name):
    """Get data from json file as string"""
    json_data = ''
    json_path = json_file_path(project, test_name)
    if os.path.isfile(json_path):
        with open(json_path, encoding='utf-8') as f:
            json_data = f.read()
    return json_data


def remove_json_data_if_present(project, test_name):
    """Remove json data file from tests/ folder"""
    json_path = json_file_path(project, test_name)
    if os.path.isfile(json_path):
        os.remove(json_path)


def validate_internal_data(internal_data_str):
    """Validate that internal data string of Python code
    does not contain SyntaxError
    """
    try:
        ast.parse(internal_data_str, filename='')
    except SyntaxError:
        return [traceback.format_exc(limit=0)]
    return []


def get_internal_test_data_as_string(project, full_test_case_name):
    """Get test data defined inside the test itself."""
    data_str = ''
    tm = test_module.Test(project, full_test_case_name).module
    if hasattr(tm, 'data'):
        data_variable = getattr(tm, 'data')
        data_str = format_internal_data_var(data_variable)
    return data_str


def format_internal_data_var(data_var):
    """Convert data_var to a properly formatted Python code string"""
    def _format_dict(d, indent):
        dict_str = indent + '{\n'
        for key, value in d.items():
            if type(value) == str:
                v = repr(value)
            else:
                v = str(value)
            dict_str += indent + '    ' + repr(key) + ': ' + v + ',\n'
        dict_str += indent + '}'
        return dict_str

    if type(data_var) is list:
        data_str = '[\n'
        for e in data_var:
            data_str += _format_dict(e, indent='    ') + ',\n'
        data_str += ']\n'
    elif type(data_var) is dict:
        data_str = _format_dict(data_var, indent='')
    else:
        data_str = repr(data_var)
    data_str = 'data = ' + data_str
    return data_str


def get_internal_test_data(project, test_name):
    """Get test data defined inside the test itself.
    data var is ignored unless it's a dictionary or a
    list of dictionaries
    """
    test = test_module.Test(project, test_name)
    if hasattr(test.module, 'data'):
        data_var = getattr(test.module, 'data')
        if type(data_var) is dict:
            return [data_var]
        if type(data_var) is list:
            if all(type(x) is dict for x in data_var):
                return data_var
    return []


def get_test_data(project, test_name):
    """Get csv data as list of dicts; json & internal data as string"""
    return {
        'csv': get_csv_test_data(project, test_name),
        'json': get_json_test_data_as_string(project, test_name),
        'internal': get_internal_test_data_as_string(project, test_name)
    }


def get_parsed_test_data(project, test_name):
    """Get test data for test execution.
    If more than one data source exist only one will be used.
    For Json or internal data, it must be of type dictionary or list
    of dictionaries otherwise it is ignored.
    """
    csv_data = get_csv_test_data(project, test_name)
    if csv_data:
        return csv_data
    json_data = get_json_test_data(project, test_name)
    if json_data:
        return json_data
    internal_data = get_internal_test_data(project, test_name)
    if internal_data:
        return internal_data
    return [{}]
