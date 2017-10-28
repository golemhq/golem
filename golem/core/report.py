"""Generate the report structure, json and screenshots"""
import json
import os
import uuid


def create_suite_execution_directory(workspace, project, suite_name, timestamp):
    execution_directory = os.path.join(workspace, 'projects', project, 'reports',
                                       suite_name, timestamp)
    if not os.path.isdir(execution_directory):
        try:
            os.makedirs(execution_directory)
        except:
            pass
    return execution_directory


def create_test_execution_directory(workspace, project, test_name, timestamp):
    execution_directory = os.path.join(workspace, 'projects', project, 'reports',
                                       'single_tests', test_name, timestamp)
    if not os.path.isdir(execution_directory):
        try:
            os.makedirs(execution_directory)
        except:
            pass
    return execution_directory


def create_report_directory(execution_directory, test_case_name, is_suite):
    set_name = 'set_' + str(uuid.uuid4())[:6]

    # create suite execution folder in reports directory
    if is_suite:
        report_directory = os.path.join(execution_directory, test_case_name, set_name)
    else:
        report_directory = os.path.join(execution_directory, set_name)

    if not os.path.isdir(report_directory):
        try:
            os.makedirs(report_directory)
        except:
            pass
    return report_directory


def generate_report(report_directory, test_case_name, test_data, result):
    json_report_path = os.path.join(report_directory, 'report.json')

    short_error = ''
    if result['error']:
        short_error = '\n'.join(result['error'].split('\n')[-2:])

    serializable_data = {}
    for key, value in test_data.items():
        try:
            json.dumps('{"{}":"{}"}'.format(key, value))
            serializable_data[key] = value
        except:
            serializable_data[key] = repr(value)
    
    env_name = ''
    if 'env' in test_data:
        if 'name' in test_data.env:
            env_name = test_data.env.name

    browser = result['browser']
    output_browser = result['browser']
    if result['browser_full_name']:
        output_browser = '{} - {}'.format(result['browser'], result['browser_full_name'])
    elif browser == 'chrome-remote':
        output_browser = 'chrome (remote)'
    elif browser == 'chrome-headless':
        output_browser = 'chrome (headless)'
    elif browser == 'chrome-remote-headless':
        output_browser = 'chrome (remote, headless)'
    elif browser == 'firefox-remote':
        output_browser = 'firefox (remote)'

    # cast steps to str
    steps = [str(x) for x in result['steps']]

    report = {
        'test_case': test_case_name,
        'result': result['result'],
        'steps': steps,
        'description': result['description'],
        'error': result['error'],
        'short_error': short_error,
        'test_elapsed_time': result['test_elapsed_time'],
        'test_timestamp': result['test_timestamp'],
        'browser': output_browser,
        'test_data': serializable_data,
        'environment': env_name,
        'set_name': result['set_name']
    }

    with open(json_report_path, 'w', encoding='utf-8') as json_file:
        json.dump(report, json_file, indent=4)
