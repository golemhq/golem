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

    print test_case_name
