"""Generate the report structure, json and screenshots"""
import json
import os
import uuid


def create_report_directory(workspace, project, test_case_name, suite_name, timestamp):
    set_name = 'set_' + str(uuid.uuid4())[:6]

    # create suite execution folder in reports directory
    if suite_name:
        report_directory = os.path.join(workspace, 'projects', project, 'reports',
                                        suite_name, timestamp, test_case_name, set_name)
    else:
        report_directory = os.path.join(workspace, 'projects', project, 'reports',
                                        'single_tests', test_case_name, timestamp, set_name)
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
    for key, value in vars(test_data).items():
        try:
            json.dumps('{"{}":"{}"}'.format(key, value))
            serializable_data[key] = value
        except:
            serializable_data[key] = repr(value)

    class MyEncoder(json.JSONEncoder):
        def default(self, obj):
            # if not isinstance(obj, Tree):
            #     return super(MyEncoder, self).default(obj)

            return obj

    report = {
        'test_case': test_case_name,
        'result': result['result'],
        'steps': result['steps'],
        'description': result['description'],
        'error': result['error'],
        'short_error': short_error,
        'test_elapsed_time': result['test_elapsed_time'],
        'test_timestamp': result['test_timestamp'],
        'browser': result['browser'],
        'test_data': serializable_data
    }
    
    with open(json_report_path, 'w', encoding='utf-8') as json_file:
        json.dump(report, json_file, indent=4)

    # save screenshots
    # no longer needed, screenshots are saved to disk when they are captured
    # for scr in result['screenshots']:
    #     img_filename = '{}.png'.format(scr)
    #     result['screenshots'][scr].save(os.path.join(report_directory, img_filename))
