import json
import os


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
        "\"default_driver\": \"chrome\",",
        "",
        "// Path to the chrome driver executable. By default it points to the",
        "// \'drivers\' folder inside the test directory.",
        "\"chrome_driver_path\": \"./drivers/chromedriver\",",
        "",
        "// Path to the gecko driver executable. This is used by Firefox.",
        "// By default it points to the 'drivers' folder inside the test directory.",
        "\"gecko_driver_path\": \"./drivers/geckodriver\",",
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
        "\"console_log_level\": \"DEBUG\",",
        "",
        "// Log all events, instead of just Golem events. Default is false",
        "\"log_all_events\": false",
        "}",
        "")
    return '\n'.join(settings_content)


def read_json_and_remove_comments(json_path):
    """What if I want to store comments in a JSON file?
    The parser is going to throw errors.
    So pass a JSON file path to tthis function and it will read it, remove the comments
    and then parse it.
    Comment lines starting with '//' are ignored"""
    with open(json_path, 'r') as json_file:
        file_lines = json_file.readlines()
        lines_without_comments = []
        for line in file_lines:
            if line.strip()[0:2] != '//' and len(line.strip()) > 0:
                lines_without_comments.append(line)
        file_content_without_comments = ''.join(lines_without_comments)
        json_data = {}
        try:
            json_data = json.loads(file_content_without_comments)
        except Exception as e:
            print('There was an error reading file {}'.format(json_path))

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
    elif settings['screenshot_on_error'] == '' or settings['screenshot_on_error'] == None:
        settings['screenshot_on_error'] = True

    if not 'screenshot_on_step' in settings:
        settings['screenshot_on_step'] = False
    elif settings['screenshot_on_step'] == '' or settings['screenshot_on_step'] == None:
        settings['screenshot_on_step'] == False

    if not 'wait_hook' in settings:
        settings['wait_hook'] = None
    elif settings['wait_hook'] == '':
        settings['wait_hook'] == None

    if not 'default_driver' in settings:
        settings['default_driver'] = 'chrome'
    elif settings['default_driver'] == '':
        settings['default_driver'] == 'chrome'

    if not 'chrome_driver_path' in settings:
        settings['chrome_driver_path'] = None
    elif settings['chrome_driver_path'] == '':
        settings['chrome_driver_path'] == None

    if not 'gecko_driver_path' in settings:
        settings['gecko_driver_path'] = None
    elif not settings['gecko_driver_path']:
        settings['gecko_driver_path'] == None

    if not 'remote_url' in settings:
        settings['remote_url'] = None
    elif not settings['remote_url']:
        settings['remote_url'] == None

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
    elif settings['log_all_events'] == '' or settings['log_all_events'] == None:
        settings['log_all_events'] = True

    return settings


def get_global_settings():
    '''get global settings from root folder'''
    settings = read_json_and_remove_comments('settings.json')
    settings = assign_settings_default_values(settings)
    return settings


def get_global_settings_as_string():
    settings_path = os.path.join('settings.json')
    settings = ''
    if os.path.isfile(settings_path):
        with open(settings_path) as settings_file:
            settings = settings_file.read()
    return settings


def get_project_settings_as_string(project):
    project_settings_path = os.path.join('projects', project, 'settings.json')
    settings = ''
    if os.path.isfile(project_settings_path):
        with open(project_settings_path) as settings_file:
            settings = settings_file.read()
    return settings


def get_project_settings(project, global_settings):
    '''get project level settings from selected project folder,
    this overrides any global settings'''
    project_settings_path = os.path.join('projects', project, 'settings.json')
    project_settings = {}
    if os.path.isfile(project_settings_path):
        project_settings = read_json_and_remove_comments(project_settings_path)
    # merge and override global settings with project settings
    for setting in project_settings:
        if project_settings[setting]:
            global_settings[setting] = project_settings[setting]

    return global_settings


def save_settings(root_path, project, project_settings, global_settings):
    settings_path = os.path.join('settings.json')
    with open(settings_path, 'w') as global_settings_file:
        global_settings_file.write(global_settings)

    project_path = os.path.join(os.path.join('projects', project, 'settings.json'))
    with open(project_path, 'w') as project_settings_file:
        project_settings_file.write(project_settings)
    return

