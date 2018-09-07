import json
import os
import traceback


SETTINGS_FILE_CONTENT = (
"""{

// Base testcase name, do not change it in a working project unless
// you know what you're doing
"base_name": "_base",

// Default timeout in seconds to wait until an element is present
"search_timeout": 20,

// Wait for elements to be present and be displayed
"wait_displayed": false,

// Take a screenshot on error
"screenshot_on_error": true,

// Take a screenshot on every step
"screenshot_on_step": false,

// Take a screenshot at the end of every test
"screenshot_on_end": false,

// Where to store test data. Options are: 'infile', 'csv'. Default is 'csv'
"test_data": "csv",

// Custom wait method to use before each step, must be defined inside extend.py
"wait_hook": null,

// Define the driver to use, unless overriden by the -d/--driver flag
"default_browser": "chrome",

// Path to the chrome driver executable.
"chromedriver_path": "./drivers/chromedriver*",

// Path to the Edge driver executable.
"edgedriver_path": "./drivers/edgedriver*",

// Path to the gecko driver executable.
"geckodriver_path": "./drivers/geckodriver*",

// Path to the ie driver executable.
"iedriver_path": "./drivers/iedriver*",

// Path to the Opera driver executable.
"operadriver_path": "./drivers/operadriver*",

// URLRemote URL : the URL to use when connecting to a remote webdriver
// for example, using selenium grid
"remote_url": "http://localhost:4444/wd/hub",

// Log level to console. Options are: DEBUG, INFO, WARNING, ERROR, CRITICAL.
// Default option is INFO
"console_log_level": "INFO",

// Log all events, instead of just Golem events. Default is true
"log_all_events": true
}
""")

REDUCED_SETTINGS_FILE_CONTENT = (
"""// Settings defined here will override global settings
{
}
""")

DEFAULTS = [
    ('base_name', None),
    ('search_timeout', 0),
    ('wait_displayed', False),
    ('screenshot_on_error', True),
    ('screenshot_on_step', False),
    ('screenshot_on_end', False),
    ('test_data', 'csv'),
    ('wait_hook', None),
    ('default_browser', 'chrome'),
    ('chromedriver_path', None),
    ('edgedriver_path', None),
    ('geckodriver_path', None),
    ('iedriver_path', None),
    ('operadriver_path', None),
    # ('safaridriver_path', None),
    ('remote_url', None),
    ('remote_browsers', {}),
    ('console_log_level', 'INFO'),
    ('log_all_events', True)
]


def create_global_settings_file(testdir):
    """Create a new global settings file"""
    print("Create global settings file")
    settings_path = os.path.join(testdir, 'settings.json')
    with open(settings_path, 'a') as settings_file:
        settings_file.write(SETTINGS_FILE_CONTENT)


def create_project_settings_file(testdir, project):
    """Create a new project settings file"""
    settings_path = os.path.join(testdir, 'projects', project, 'settings.json')
    with open(settings_path, 'a') as settings_file:
        settings_file.write(REDUCED_SETTINGS_FILE_CONTENT)


def _read_json_with_comments(json_path):
    """Reads a file with '//' comments.
    Reads the file, removes the commented lines and return
    a json loads of the result.
    """
    file_lines = []
    with open(json_path) as json_file:
        file_lines = json_file.readlines()
    lines_without_comments = []
    for line in file_lines:
        if line.strip()[0:2] != '//' and len(line.strip()) > 0:
            lines_without_comments.append(line)
    file_content_without_comments = ''.join(lines_without_comments)
    json_data = {}
    try:
        json_data = json.loads(file_content_without_comments)
    except Exception:
        print('There was an error reading file {}'.format(json_path))
        print(traceback.format_exc())
    return json_data


def assign_settings_default_values(settings):
    """Verify that each setting value is present at least with
    the default value
    """ 
    for default in DEFAULTS:
        if not default[0] in settings:
            settings[default[0]] = default[1]
        elif settings[default[0]] in ['', None]:
                settings[default[0]] = default[1]
    return settings


def _deprecated_implicit_wait_warning(settings):
    if 'implicit_wait' in settings:
        print("INFO: 'implicit_wait' setting is deprecated, use 'search_timeout' instead")
        if not 'search_timeout' in settings:
            # if implicit_wait is defined and search_timeout is not,
            # Use the value of the former for the latter
            settings['search_timeout'] = settings['implicit_wait']
    return settings


def get_global_settings(workspace):
    """Get global settings from workspace folder as a dictionary"""
    settings_path = os.path.join(workspace, 'settings.json')
    settings = {}
    if os.path.exists(settings_path):
        settings = _read_json_with_comments(settings_path)
        # TODO implicit_wait setting is deprecated
        # remove once implicit_wait is fully deprecated
        settings = _deprecated_implicit_wait_warning(settings)
        settings = assign_settings_default_values(settings)
    else:
        print('Warning: settings file is not present')
    return settings


def get_global_settings_as_string(workspace):
    """Get global settings as a string"""
    settings_path = os.path.join(workspace, 'settings.json')
    settings = ''
    if os.path.exists(settings_path):
        with open(settings_path) as settings_file:
            settings = settings_file.read()
    return settings


def get_project_settings(workspace, project):
    """Get project level settings from project directory,
    Merge global and project settings.
    Project settings override global settings
    """
    global_settings = get_global_settings(workspace)
    project_settings_path = os.path.join(workspace, 'projects',
                                         project, 'settings.json')
    project_settings = {}
    if os.path.exists(project_settings_path):
        project_settings = _read_json_with_comments(project_settings_path)
        # TODO implicit_wait setting is deprecated
        # remove once implicit_wait is fully deprecated
        project_settings = _deprecated_implicit_wait_warning(project_settings)
    # merge and override global settings with project settings
    for setting in project_settings:
        global_settings[setting] = project_settings[setting]
    global_settings = assign_settings_default_values(global_settings)
    return global_settings


def get_project_settings_as_string(workspace, project):
    """Get project settings as a string"""
    project_settings_path = os.path.join(workspace, 'projects',
                                         project, 'settings.json')
    settings = ''
    if os.path.exists(project_settings_path):
        with open(project_settings_path) as settings_file:
            settings = settings_file.read()
    return settings


def save_global_settings(workspace, global_settings):
    """Save global settings.
    input settings must be to be the string content of file."""
    settings_path = os.path.join(workspace, 'settings.json')
    if global_settings is not None:
        with open(settings_path, 'w') as global_settings_file:
            global_settings_file.write(global_settings)


def save_project_settings(workspace, project, project_settings):
    """Save project settings.
    input settings must be to be the string content of file."""
    project_path = os.path.join(workspace, 'projects', project, 'settings.json')
    with open(project_path, 'w') as project_settings_file:
        project_settings_file.write(project_settings)


def get_remote_browsers(settings):
    """Return the defined remote browsers in settings."""
    remote_browsers = {}
    if 'remote_browsers' in settings:
        remote_browsers = settings['remote_browsers']
    return remote_browsers


def get_remote_browser_list(settings):
    """Return a list of the remote browsers defined in settings."""
    remote_browser_list = list(get_remote_browsers(settings).keys())
    return remote_browser_list
