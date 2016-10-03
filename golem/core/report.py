import json
import os


def create_report_directory(workspace,
                            project,
                            test_case_name,
                            suite_name,
                            timestamp):

    # create suite execution folder in reports directory
    execution_path = os.path.join(workspace,
                                  'projects',
                                  project,
                                  'reports',
                                  suite_name,
                                  timestamp,
                                  test_case_name)

    if not os.path.isdir(execution_path):
        try:
            os.makedirs(execution_path)
        except:
            pass

    return execution_path


def generate_report(report_directory, test_case_name, test_data, result):
    
    json_report_path = os.path.join(report_directory, 'report.json')

    report = {
        'test_case': test_case_name,
        'result': result['result'],
        'steps': result['steps'],
        'description': result['description'],
        'error': result['error'],
        'test_elapsed_time': result['test_elapsed_time'],
        'test_timestamp': result['test_timestamp']
    }
    
    with open(json_report_path, 'w') as json_file:
        json.dump(report, json_file, indent=4)

    # save screenshots
    for scr in result['screenshots']:
        img_filename = '{}.png'.format(scr)
        result['screenshots'][scr].save(os.path.join(report_directory,
                                                     img_filename))
