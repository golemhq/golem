"""Generate report for test execution"""
import json
import os
import uuid


def create_execution_directory(workspace, project, timestamp,
                               test_name=None, suite_name=None):
    """Create directory to store report for suite or single test.
    
    If suite, directory will be:
    <workspace>/projects/<project>/reports/<suite_name>/<timestamp>/
    
    If test, directory will be:
    <workspace>/projects/<project>/reports/single_tests/<test_name>/<timestamp>/
    """
    if test_name:
        execution_directory = os.path.join(workspace, 'projects', project,
                                           'reports', 'single_tests', test_name,
                                           timestamp)
    elif suite_name:
        execution_directory = os.path.join(workspace, 'projects', project,
                                           'reports', suite_name, timestamp)
    else:
        # TODO
        import sys
        sys.exit('Invalid params for create_test_execution_directory')

    if not os.path.isdir(execution_directory):
        try:
            os.makedirs(execution_directory)
        except:
            pass
    return execution_directory


def create_report_directory(execution_directory, test_case_name, is_suite):
    """Create direcoty to store a single test report.
    
    execution_directory takes the following format for suites:
      <workspace>/projects/<project>/reports/<suite_name>/<timestamp>/
    and this format for single tests
      <workspace>/projects/<project>/reports/<suite_name>/<timestamp>/
    
    The result for suites is:
      <execution_directory>/<test_name>/<set_name>/
    and for single tests is:
      <execution_directory>/<set_name>/
    """
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
    """Generate the json report for a single test execution."""
    json_report_path = os.path.join(report_directory, 'report.json')
    # short_error = ''
    # if result['error']:
    #     short_error = '\n'.join(result['error'].split('\n')[-2:])

    # TODO
    serialized_data = {}
    for key, value in test_data.items():
        try:
            json.dumps('{"{}":"{}"}'.format(key, value))
            serialized_data[key] = value
        except:
            serialized_data[key] = repr(value)
    
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

    report = {
        'test_case': test_case_name,
        'result': result['result'],
        'steps': result['steps'],
        'errors': result['errors'],
        'description': result['description'],
        'browser': output_browser,
        'test_data': serialized_data,
        'environment': env_name,
        'set_name': result['set_name'],
        'test_elapsed_time': result['test_elapsed_time'],
        'test_timestamp': result['test_timestamp']
    }
    with open(json_report_path, 'w', encoding='utf-8') as json_file:
        json.dump(report, json_file, indent=4)
