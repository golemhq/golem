"""Helper general purpose functions"""
import glob
import importlib
import json
import os
import re
import shutil
import traceback
from datetime import datetime
from distutils.version import StrictVersion

from golem.core import file_manager, session


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
    return file, parents


def delete_element(project, element_type, dot_path):
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
    path = os.path.join(session.testdir, 'projects', project, folder,
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
        data_path = os.path.join(session.testdir, 'projects', project, 'data',
                                 dot_path.replace('.', os.sep) + '.csv')
        try:
            os.remove(data_path)
        except:
            pass
        data_path = os.path.join(session.testdir, 'projects', project, 'tests',
                                 dot_path.replace('.', os.sep) + '.csv')
        try:
            os.remove(data_path)
        except:
            pass

    return errors


def duplicate_element(project, element_type, original_file_dot_path, new_file_dot_path):
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
        for c in new_file_dot_path.replace('.', ''):
            if not c.isalnum() and c != '_':
                errors.append('Only letters, numbers and underscores are allowed')
                break

    if not errors:
        root_path = os.path.join(session.testdir, 'projects', project)
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


def choose_browser_by_precedence(cli_browsers=None, suite_browsers=None,
                                 settings_default_browser=None):
    """ Defines which browser(s) to use by order of precedence
    The order is the following:
    1. browsers defined by CLI
    2. browsers defined inside a suite
    3. 'default_driver' setting
    4. chrome
    """
    if cli_browsers:
        browsers = cli_browsers
    elif suite_browsers:
        browsers = suite_browsers
    elif settings_default_browser:
        browsers = [settings_default_browser]
    else:
        browsers = ['chrome']  # default default
    return browsers


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


def import_module(path):
    """Import a Python module from a given path"""
    mod = None
    error = None
    module_dir, module_file = os.path.split(path)
    module_name, module_ext = os.path.splitext(module_file)
    try:
        spec = importlib.util.spec_from_file_location(module_name, path)
        # Note: module_from_spec is new in python 3.5
        if hasattr(importlib.util, 'module_from_spec'):
            _mod = importlib.util.module_from_spec(spec)
        else:
            _mod = spec.loader.load_module()
        spec.loader.exec_module(_mod)
        mod = _mod
    except:
        error = traceback.format_exc(limit=0)
    return mod, error


def extract_version_from_webdriver_filename(filename):
    """Extract version from webdriver filename.
    
    Expects a file in the format: `filename_1.2` or `filename_1.2.exe`
    The extracted version must conform with pep-386
    If a valid version is not found it returns '0.0'
    """
    version = '0.0'
    if '_' in filename:
        components = filename.replace('.exe', '').split('_')
        if len(components) > 1:
            parsed_version = components[-1]
            try:
                StrictVersion(parsed_version)
                version = parsed_version
            except:
                pass
    return version


def match_latest_executable_path(glob_path):
    """Returns the absolute path to the webdriver executable
    with the highest version given a path with glob pattern.
    """
    found_files = []
    absolute_glob_path = os.path.abspath(glob_path)
    # Note: recursive=True arg is not supported
    # in Python 3.4, so '**' wildcard is not supported
    matched_files = glob.glob(absolute_glob_path)
    for matched_file in matched_files:
        found_files.append((matched_file, extract_version_from_webdriver_filename(matched_file)))
    if found_files:
        highest_version = sorted(found_files, key=lambda tup: StrictVersion(tup[1]), reverse=True)
        return highest_version[0][0]
    else:
        return None


def get_valid_filename(s):
    """Receives a string and returns a valid filename"""
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)


def prompt_yes_no(question, default=True):
    """Prompt the user through the console for yes or no"""
    while True:
        choice = input(question).lower()
        if choice in ['yes', 'y']:
            return True
        elif choice in ['no', 'n']:
            return False
        elif not choice:
            return default


class ImmutableKeysDict(dict):
    """A dictionary where keys cannot be added after instantiation"""

    def __setitem__(self, key, value):
        if key not in self:
            raise AttributeError("cannot add new keys to ImmutableKeysDict")
        dict.__setitem__(self, key, value)


def validate_email(email):
    """Validate email address"""
    re_str = r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$'
    match = re.match(re_str, email)
    return match is not None
