import os

def get_data(content):
    key_value_pairs = {}

    for line in content:
        if '=' in line:
            key = line.split('=')[0].strip()
            value = line.split('=')[1].strip().replace('\'','').replace('\"', '')
            key_value_pairs[key] = value
    return key_value_pairs


def parse_test_data(root_path, project, parents, test_case_name):

    parents_joined = os.sep.join(parents)

    path = os.path.join(
        root_path, 'projects', project, 'data', parents_joined, test_case_name + '.py')

    with open(path) as f:
        content = f.readlines()

    key_value_pairs = get_data(content)

    return key_value_pairs


def save_test_data(root_path, project, test_case_name, test_data):
    test_case_path = os.path.join(
        root_path, 'projects', project, 'data', test_case_name + '.py')

    with open(test_case_path, 'w') as f:
        for data in test_data:
            print data
            f.write('{} = \'{}\'\n'.format(data['variable'], data['value']))

def is_data_variable(root_path, project, parents, test_case_name, parameter_name):
    test_data_variables = parse_test_data(root_path, project, parents, test_case_name)
    if parameter_name in test_data_variables:
        return True
    else: 
        return False