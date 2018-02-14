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
                                  ['subdir1', 'subdir2'], 'test3')
        page_object.new_page_object(testdir_fixture['path'],
                                  project_fixture['name'],
                                  ['subdir1'], 'test2')
        page_object.new_page_object(testdir_fixture['path'],
                                  project_fixture['name'], [], 'test1')
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
        suite.new_suite(testdir_fixture['path'], project_fixture['name'],
                        [], 'suite1')
        suite.new_suite(testdir_fixture['path'], project_fixture['name'],
                        [], 'suite2')
        
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

