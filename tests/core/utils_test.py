import os
from collections import OrderedDict
from subprocess import call

from golem.core import utils, page_object, test_case, suite

from tests.fixtures import project_class, testdir_session
from tests import helper_functions


class Test_get_test_cases:

    def test_get_test_cases(self, project_class):
        testdir = project_class['testdir']
        test_case.new_test_case(testdir,
                                project_class['name'],
                                ['subdir1', 'subdir2'],
                                'test3')
        test_case.new_test_case(testdir,
                                project_class['name'],
                                ['subdir1'],
                                'test2')
        test_case.new_test_case(testdir,
                                project_class['name'],
                                [],
                                'test1')
        tests = utils.get_test_cases(testdir,
                                     project_class['name'])
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

    def test_get_pages(self, project_class):
        testdir = project_class['testdir']
        page_object.new_page_object(testdir,
                                  project_class['name'],
                                  ['subdir1', 'subdir2'], 'test3')
        page_object.new_page_object(testdir,
                                  project_class['name'],
                                  ['subdir1'], 'test2')
        page_object.new_page_object(testdir,
                                    project_class['name'],
                                    [], 'test1')
        pages = utils.get_pages(testdir,
                                project_class['name'])

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

    def test_get_suites(self, project_class):
        testdir = project_class['testdir']
        suite.new_suite(testdir, project_class['name'],
                        [], 'suite1')
        suite.new_suite(testdir, project_class['name'],
                        [], 'suite2')
        
        suites = utils.get_suites(testdir,
                                  project_class['name'])
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

    def test_get_projects(self, project_class):
        projects = utils.get_projects(project_class['testdir'])
        assert project_class['name'] in projects


class Test_project_exists:
    
    def test_project_exists(self, project_class):
        exists = utils.project_exists(project_class['testdir'],
                                      project_class['name'])
        assert exists

