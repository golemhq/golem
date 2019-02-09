import json
import os
import sys
import time

from golem.core import utils, file_manager


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


def get_tests_tags(workspace, project, tests):
    """Get the tags of a list of tests

    Caches the results.
    Updates the cache when last modification time of file is greater
    than cache timestamp
    """
    cache_file_path = os.path.join(workspace, 'projects', project, '.tags')
    cache_tags = {}
    if os.path.isfile(cache_file_path):
        with open(cache_file_path) as f:
            cache_tags = json.load(f)
    for test in tests:
        if test in cache_tags:
            # check if test file modification date > cache file timestamp:
            cache_timestamp = cache_tags[test]['timestamp']
            tc_name, parents = utils.separate_file_from_parents(test)
            path = os.path.join(workspace, 'projects', project, 'tests',
                                os.sep.join(parents), '{}.py'.format(tc_name))
            last_modified_time = os.path.getmtime(path)
            if last_modified_time > cache_timestamp:
                # re-read tags
                timestamp = time.time()
                cache_tags[test] = {
                    'tags': get_test_tags(workspace, project, test),
                    'timestamp': timestamp
                }
        else:
            timestamp = time.time()
            cache_tags[test] = {
                'tags': get_test_tags(workspace, project, test),
                'timestamp': timestamp
            }
    with open(cache_file_path, 'w') as f:
        json.dump(cache_tags, f, indent=4)
    tags = {test: cache_tags[test]['tags'] for test in cache_tags}
    return tags


def get_all_project_tests_tags(workspace, project):
    """Get all the tags of each test in a project"""
    tests_folder_path = os.path.join(workspace, 'projects', project, 'tests')
    tests = file_manager.get_files_dot_path(tests_folder_path, extension='.py')
    return get_tests_tags(workspace, project, tests)


def get_project_unique_tags(workspace, project):
    """Get a list of the unique tags used by all the tests of a project"""
    tests_tags = get_all_project_tests_tags(workspace, project)
    unique_tags = []
    for test, tags in tests_tags.items():
        for tag in tags:
            if tag not in unique_tags:
                unique_tags.append(tag)
    return unique_tags
