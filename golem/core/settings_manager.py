import json
import os
import traceback


def settings_file_content():
    settings_content = (
        "{",
        "// Default time to wait looking for an element until it is found",
        "\"implicit_wait\": 20,",
        "",
        "// Take a screenshot on error by default",
        "\"screenshot_on_error\": true,",
        "",
        "// Take a screenshot on every step",
        "\"screenshot_on_step\": false,",
        "",
        "// Custom wait method to use before each step, must be defined inside extend.py",
        "\"wait_hook\": null,",
        "",
        "// Define the driver to use, unless overriden by the -d/--driver flag",
        "\"default_browser\": \"chrome\",",
        "",
        "// Path to the chrome driver executable. By default it points to the",
        "// \'drivers\' folder inside the test directory.",
        "\"chromedriver_path\": \"./drivers/chromedriver\",",
        "",
        "// Path to the gecko driver executable. This is used by Firefox.",
        "// By default it points to the 'drivers' folder inside the test directory.",
        "\"geckodriver_path\": \"./drivers/geckodriver\",",
        "",
        "// Path to the ie driver executable. This is used by Internet Explorer.",
        "// By default it points to the 'drivers' folder inside the test directory.",
        "\"iedriver_path\": \"./drivers/iedriver.exe\",",
        "",
        "// URLRemote URL : the URL to use when connecting to a remote webdriver",
        "// for example, using selenium grid",
        "\"remote_url\": \"http://localhost:4444/wd/hub\",",
        "",
        "// Log level to console. Options are: DEBUG, INFO, WARNING, ERROR, CRITICAL.",
        "// Default option is INFO",
        "\"console_log_level\": \"INFO\",",
        "",
        "// Log level to file. Options are: DEBUG, INFO, WARNING, ERROR, CRITICAL.",
        "// Default option is DEBUG",
        "\"file_log_level\": \"DEBUG\",",
        "",
        "// Log all events, instead of just Golem events. Default is false",
        "\"log_all_events\": false",
        "}",
        "")
    return '\n'.join(settings_content)


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


def reduced_settings_file_content():
    settings_content = (
        "// Settings defined here will override global settings\n"
        "{\n"
        "}\n")
    return settings_content


def assign_settings_default_values(settings):
    if not 'implicit_wait' in settings:
        settings['implicit_wait'] = None
    elif settings['implicit_wait'] == '':
        settings['implicit_wait'] = None

    if not 'screenshot_on_error' in settings:
        settings['screenshot_on_error'] = True
    elif settings['screenshot_on_error'] == '' or settings['screenshot_on_error'] is None:
        settings['screenshot_on_error'] = True

    if not 'screenshot_on_end' in settings:
        settings['screenshot_on_end'] = False
    elif settings['screenshot_on_end'] == '' or settings['screenshot_on_end'] is None:
        settings['screenshot_on_end'] = False

    if not 'screenshot_on_step' in settings:
        settings['screenshot_on_step'] = False
    elif settings['screenshot_on_step'] == '' or settings['screenshot_on_step'] is None:
        settings['screenshot_on_step'] = False

    if not 'wait_hook' in settings:
        settings['wait_hook'] = None
    elif settings['wait_hook'] == '':
        settings['wait_hook'] = None

    if not 'default_browser' in settings:
        settings['default_browser'] = 'chrome'
    elif settings['default_browser'] == '':
        settings['default_browser'] = 'chrome'

    if not 'chromedriver_path' in settings:
        settings['chromedriver_path'] = None
    elif settings['chromedriver_path'] == '':
        settings['chromedriver_path'] = None

    if not 'geckodriver_path' in settings:
        settings['geckodriver_path'] = None
    elif not settings['geckodriver_path']:
        settings['geckodriver_path'] = None

    if not 'iedriver_path' in settings:
        settings['iedriver_path'] = None
    elif not settings['iedriver_path']:
        settings['iedriver_path'] = None

    if not 'remote_url' in settings:
        settings['remote_url'] = None
    elif not settings['remote_url']:
        settings['remote_url'] = None

    if not 'remote_browsers' in settings:
        settings['remote_browsers'] = {}
    elif not settings['remote_browsers']:
        settings['remote_browsers'] = {}

    if not 'console_log_level' in settings:
        settings['console_log_level'] = 'INFO'
    elif not settings['console_log_level']:
        settings['console_log_level'] = 'INFO'

    if not 'file_log_level' in settings:
        settings['file_log_level'] = 'DEBUG'
    elif not settings['file_log_level']:
        settings['file_log_level'] = 'DEBUG'

    if not 'log_all_events' in settings:
        settings['log_all_events'] = True
    elif settings['log_all_events'] == '' or settings['log_all_events'] is None:
        settings['log_all_events'] = True

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
