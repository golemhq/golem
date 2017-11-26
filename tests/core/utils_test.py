import os
from collections import OrderedDict
from subprocess import call

from golem.core import utils, page_object, test_case, suite

from tests.fixtures import project_fixture, testdir_fixture
from tests import helper_functions


class Test_get_test_cases:

    def test_get_test_cases(self, testdir_fixture, project_fixture):
        test_case.new_test_case(testdir_fixture['path'],
                                project_fixture['name'],
                                ['subdir1', 'subdir2'],
                                'test3')
        test_case.new_test_case(testdir_fixture['path'],
                                project_fixture['name'],
                                ['subdir1'],
                                'test2')
        test_case.new_test_case(testdir_fixture['path'],
                                project_fixture['name'],
                                [],
                                'test1')
        tests = utils.get_test_cases(testdir_fixture['path'],
                                     project_fixture['name'])


        expected_result = {
            'type': 'directory',
            'name': 'tests',
            'dot_path': '.',
            'sub_elements': [
                {
                    'type': 'directory',
                    'name': 'subdir1',
                    'dot_path': 'subdir1',
                    'sub_elements': [
                        {
                            'type': 'directory',
                            'name': 'subdir2',
                            'dot_path': 'subdir1.subdir2',
                            'sub_elements': [
                                {
                                    'type': 'file',
                                    'name': 'test3',
                                    'dot_path': 'subdir1.subdir2.test3',
                                    'sub_elements': []
                                }
                            ]
                        },
                        {
                            'type': 'file',
                            'name': 'test2',
                            'dot_path': 'subdir1.test2', 'sub_elements': []
                        }
                    ]
                },
                {
                    'type': 'file',
                    'name': 'test1',
                    'dot_path': 'test1',
                    'sub_elements': []
                }
            ]
        }

        assert tests == expected_result


class Test_get_pages:

    def test_get_pages(self, testdir_fixture, project_fixture):
        page_object.new_page_object(testdir_fixture['path'],
                                  project_fixture['name'],
                                  ['subdir1', 'subdir2'],
                                  'test3',
                                  add_parents=True)
        page_object.new_page_object(testdir_fixture['path'],
                                  project_fixture['name'],
                                  ['subdir1'],
                                  'test2',
                                  add_parents=True)
        page_object.new_page_object(testdir_fixture['path'],
                                  project_fixture['name'],
                                  [],
                                  'test1',
                                  add_parents=True)
        pages = utils.get_pages(testdir_fixture['path'],
                                       project_fixture['name'])

        expected_result = {
            'type': 'directory',
            'name': 'pages',
            'dot_path': '.',
            'sub_elements': [
                {
                    'type': 'directory',
                    'name': 'subdir1',
                    'dot_path': 'subdir1',
                    'sub_elements': [
                        {
                            'type': 'directory',
                            'name': 'subdir2',
                            'dot_path': 'subdir1.subdir2',
                            'sub_elements': [
                            {
                                'type': 'file',
                                'name': 'test3',
                                'dot_path': 'subdir1.subdir2.test3',
                                'sub_elements': []
                            }
                        ]
                        },
                        {
                            'type': 'file',
                            'name': 'test2',
                            'dot_path': 'subdir1.test2',
                            'sub_elements': []
                        }
                    ]
                },
                {
                    'type': 'file',
                    'name': 'test1',
                    'dot_path': 'test1',
                    'sub_elements': []
                }
            ]
        }
        assert pages == expected_result


class Test_get_suites:

    def test_get_suites(self, testdir_fixture, project_fixture):
        suite.new_suite(testdir_fixture['path'],
                        project_fixture['name'],
                        [],
                        'suite1')
        suite.new_suite(testdir_fixture['path'],
                        project_fixture['name'],
                        [],
                        'suite2')
        
        suites = utils.get_suites(testdir_fixture['path'],
                                  project_fixture['name'])
        expected_result = {
            'type': 'directory',
            'name': 'suites',
            'dot_path': '.',
            'sub_elements': [
                {
                    'type': 'file',
                    'name': 'suite1',
                    'dot_path': 'suite1',
                    'sub_elements': []
                },
                {
                    'type': 'file',
                    'name': 'suite2',
                    'dot_path': 'suite2',
                    'sub_elements': []
                }
            ]
        }
        assert suites == expected_result


class Test_get_projects:

    def test_get_projects(self, project_fixture, testdir_fixture):
        projects = utils.get_projects(testdir_fixture['path'])
        assert project_fixture['name'] in projects


class Test_project_exists:
    
    def test_project_exists(self, project_fixture, testdir_fixture):
        exists = utils.project_exists(testdir_fixture['path'],
                                      project_fixture['name'])
        assert exists


class Test_get_files_in_directory_dot_path:

    def test_get_files_in_directory_dot_path(self, testdir_fixture):
        project = helper_functions.create_random_project(testdir_fixture['path'])
        # create a new page object in pages folder
        page_object.new_page_object(testdir_fixture['path'],
                                    project,
                                    [],
                                    'page1')
        # create a new page object in pages/dir/subdir/
        page_object.new_page_object(testdir_fixture['path'],
                                    project,
                                    ['dir', 'subdir'],
                                    'page2',
                                    add_parents=True)
        base_path = os.path.join(testdir_fixture['path'],
                                 'projects',
                                 project,
                                 'pages')
        dotted_files = utils.get_files_in_directory_dot_path(base_path)
        assert 'page1' in dotted_files
        assert 'dir.subdir.page2' in dotted_files
        assert len(dotted_files) == 2


