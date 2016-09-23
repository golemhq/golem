import json
import os


def generate_report(result,
                    workspace,
                    project,
                    test_case_name,
                    test_data,
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

    report = {
        'test_case': test_case_name,
        'result': result['result'],
        'steps': result['steps'],
        'description': result['description'],
        'error': result['error'],
    }

    report_path = os.path.join(execution_path, 'report.json')
    
    with open(report_path, 'w') as json_file:
        json.dump(report, json_file, indent=4)

