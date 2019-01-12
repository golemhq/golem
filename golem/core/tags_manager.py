from golem.core import utils
import os
import sys


def filter_tests_by_tags(workspace, project, tests, tags):
    result = []

    for test in tests:
        tags_in_test = get_test_tags(workspace, project, test)

        if set(tags) & set(tags_in_test):
            result.append(test)

    if len(result) > 0:
        return result
    else:
        sys.exit("No tests found with tag(s): {}".format(tags))


def get_test_tags(workspace, project, full_test_case_name):
    result = []
    tc_name, parents = utils.separate_file_from_parents(full_test_case_name)
    path = os.path.join(workspace, 'projects', project, 'tests',
                        os.sep.join(parents), '{}.py'.format(tc_name))
    test_module, _ = utils.import_module(path)

    if hasattr(test_module, 'tags'):
        result = getattr(test_module, 'tags')

    return result
