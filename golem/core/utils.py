"""Helper general purpose functions"""
import glob
import importlib
import json
import os
import re
import traceback
import types
from datetime import datetime
from distutils.version import StrictVersion


def get_timestamp():
    time_format = "%Y.%m.%d.%H.%M.%S.%f"
    timestamp = datetime.today().strftime(time_format)
    # remove last 3 decimal places from microseconds
    timestamp = timestamp[:-3]
    return timestamp


def get_date_from_timestamp(timestamp):
    date = datetime.strptime(timestamp, '%Y.%m.%d.%H.%M.%S.%f')
    return date


def get_date_time_from_timestamp(timestamp):
    """Get the date time from a timestamp.

    The timestamp must have the following format:
    'year.month.day.hour.minutes'
    Example:
    '2017.12.20.10.31' -> '2017/12/20 10:31'
    """
    date_time_string = timestamp
    sp = timestamp.split('.')
    if len(sp) >= 5:
        date_time_string = '{0}/{1}/{2} {3}:{4}'.format(sp[0], sp[1], sp[2], sp[3], sp[4])
    return date_time_string


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
    with open(filepath, encoding='utf-8') as json_file:
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
        _mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_mod)
        mod = _mod
    except:
        error = traceback.format_exc(limit=0)
    return mod, error


def module_local_public_functions(module):
    """Get a list of function names defined in a module.
    Ignores functions that start with `_` and functions
    imported from other modules.
    """
    local_functions = []
    module_name = module.__name__
    for name in dir(module):
        if not name.startswith('_'):
            attr = getattr(module, name)
            if isinstance(attr, types.FunctionType) and attr.__module__ == module_name:
                local_functions.append(name)
    return local_functions


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


def match_latest_executable_path(glob_path, testdir):
    """Returns the absolute path to the webdriver executable
    with the highest version given a path with glob pattern.
    """
    found_files = []
    glob_path = os.path.normpath(glob_path)
    if not os.path.isabs(glob_path):
        glob_path = os.path.join(testdir, glob_path)
    # Note: recursive=True arg is not supported
    # in Python 3.4, so '**' wildcard is not supported
    matched_files = [x for x in glob.glob(glob_path) if os.path.isfile(x)]
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


def normalize_query(path):
    """Normalize a relative path to a suite or test
    to a dotted relative path
    """
    normalized = os.path.normpath(path)
    if '.py' in normalized:
        normalized = os.path.splitext(normalized)[0]
    if os.sep in normalized:
        normalized = normalized.replace(os.sep, '.')
    return normalized
