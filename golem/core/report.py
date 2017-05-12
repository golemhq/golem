import json
import os
import uuid


def create_report_directory(workspace, project, test_case_name,
                            suite_name, timestamp):
    
    # if not suite_name:
    #     suite_name = '__single__'

    set_name = 'set_' + str(uuid.uuid4())[:6]

    # create suite execution folder in reports directory
    if suite_name:
        report_directory = os.path.join(workspace, 'projects', project,
                                   'reports', suite_name, timestamp,
                                   test_case_name, set_name)
    else:
        report_directory = os.path.join(workspace, 'projects', project,
                                   'reports', '__single__', test_case_name,
                                   timestamp, set_name)

    if not os.path.isdir(report_directory):
        try:
            os.makedirs(report_directory)
        except:
            pass

    return report_directory


def generate_report(report_directory, test_case_name, test_data, result):
    
    json_report_path = os.path.join(report_directory, 'report.json')

    if result['error']:
        short_error = '\n'.join(result['error'].split('\n')[-2:])
    else:
        short_error = ''

    report = {
        'test_case': test_case_name,
        'result': result['result'],
        'steps': result['steps'],
        'description': result['description'],
        'error': result['error'],
        'short_error': short_error,
        'test_elapsed_time': result['test_elapsed_time'],
        'test_timestamp': result['test_timestamp'],
        'browser': result['browser']
    }
    
    with open(json_report_path, 'w', encoding='utf-8') as json_file:
        json.dump(report, json_file, indent=4)

    # save screenshots
    for scr in result['screenshots']:
        img_filename = '{}.png'.format(scr)
        result['screenshots'][scr].save(os.path.join(report_directory,
                                                     img_filename))
