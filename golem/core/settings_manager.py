import json
import os
import traceback


SETTINGS_FILE_CONTENT = (
"""{
// Default time to wait looking for an element until it is found
"implicit_wait": 20,

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

// Path to the chrome driver executable. By default it points to the
// 'drivers' folder inside the test directory.
"chromedriver_path": "./drivers/chromedriver",

// Path to the gecko driver executable. This is used by Firefox.
// By default it points to the 'drivers' folder inside the test directory.
"geckodriver_path": "./drivers/geckodriver",

// Path to the ie driver executable. This is used by Internet Explorer.
// By default it points to the 'drivers' folder inside the test directory.
"iedriver_path": "./drivers/iedriver.exe",

// URLRemote URL : the URL to use when connecting to a remote webdriver
// for example, using selenium grid
"remote_url": "http://localhost:4444/wd/hub",

// Log level to console. Options are: DEBUG, INFO, WARNING, ERROR, CRITICAL.
// Default option is INFO
"console_log_level": "INFO",

// Log level to file. Options are: DEBUG, INFO, WARNING, ERROR, CRITICAL.
// Default option is DEBUG
"file_log_level": "DEBUG",

// Log all events, instead of just Golem events. Default is false
"log_all_events": "false"
}
""")

REDUCED_SETTINGS_FILE_CONTENT = (
"""// Settings defined here will override global settings
{
}
""")


def read_json_with_comments(json_path):
    """Receives a list of lines of a json file with '//' comments
    Remove the commented lines and return a json loads of the result
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
    """ Verify that each setting value is present at least with
    the default value""" 
    defaults = [
        ('implicit_wait', None),
        ('screenshot_on_error', True),
        ('screenshot_on_step', False),
        ('screenshot_on_end', False),
        ('test_data', 'csv'),
        ('wait_hook', None),
        ('default_browser', 'chrome'),
        ('chromedriver_path', None),
        ('geckodriver_path', None),
        ('iedriver_path', None),
        ('remote_url', None),
        ('remote_browsers', {}),
        ('console_log_level', 'INFO'),
        ('file_log_level', 'DEBUG'),
        ('log_all_events', False)
    ]

    for default in defaults:
        if not default[0] in settings:
            settings[default[0]] = default[1]
        elif settings[default[0]] in ['', None]:
                settings[default[0]] = default[1]

    return settings


def get_global_settings(workspace):
    '''get global settings from workspace folder'''
    settings_path = os.path.join(workspace, 'settings.json')
    settings = {}
    if os.path.exists(settings_path):
        settings = read_json_with_comments(settings_path)
        settings = assign_settings_default_values(settings)
    else:
        print('Warning: settings file is not present')
    return settings


def get_global_settings_as_string(workspace):
    settings_path = os.path.join(workspace, 'settings.json')
    settings = ''
    if os.path.exists(settings_path):
        with open(settings_path) as settings_file:
            settings = settings_file.read()
    return settings


def get_project_settings_as_string(workspace, project):
    project_settings_path = os.path.join(workspace, 'projects',
                                         project, 'settings.json')
    settings = ''
    if os.path.exists(project_settings_path):
        with open(project_settings_path) as settings_file:
            settings = settings_file.read()
    return settings


def get_project_settings(workspace, project):
    '''get project level settings from selected project folder,
    this overrides any global settings'''
    global_settings = get_global_settings(workspace)
    project_settings_path = os.path.join(workspace, 'projects',
                                         project, 'settings.json')
    project_settings = {}
    if os.path.exists(project_settings_path):
        project_settings = read_json_with_comments(project_settings_path)
        project_settings = assign_settings_default_values(project_settings)
    # merge and override global settings with project settings
    for setting in project_settings:
        if project_settings[setting]:
            global_settings[setting] = project_settings[setting]
    return global_settings


def save_settings(project, project_settings, global_settings):
    settings_path = os.path.join('settings.json')
    with open(settings_path, 'w') as global_settings_file:
        global_settings_file.write(global_settings)

    if project is not None and project_settings is not None:
        project_path = os.path.join('projects', project, 'settings.json')
        with open(project_path, 'w') as project_settings_file:
            project_settings_file.write(project_settings)
    return


def get_remote_browsers(settings):
    remote_browsers = list(settings['remote_browsers'].keys())
    return remote_browsers
