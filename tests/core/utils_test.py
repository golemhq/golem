import os
from collections import OrderedDict

from golem.core import utils
from golem.gui import page_object, test_case, suite

from tests.fixtures import project_fixture, test_directory_fixture


class Test_get_test_cases:

    def test_get_test_cases(self, test_directory_fixture, project_fixture):
        test_case.new_test_case(test_directory_fixture['full_path'],
                                project_fixture['project_name'],
                                ['subdir1', 'subdir2'],
                                'test3')
        test_case.new_test_case(test_directory_fixture['full_path'],
                                project_fixture['project_name'],
                                ['subdir1'],
                                'test2')
        test_case.new_test_case(test_directory_fixture['full_path'],
                                project_fixture['project_name'],
                                [],
                                'test1')
        tests = utils.get_test_cases(test_directory_fixture['full_path'],
                                     project_fixture['project_name'])


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


class Test_get_page_objects:

    def test_get_page_objects(self, test_directory_fixture, project_fixture):
        page_object.new_page_object(test_directory_fixture['full_path'],
                                  project_fixture['project_name'],
                                  ['subdir1', 'subdir2'],
                                  'test3')
        page_object.new_page_object(test_directory_fixture['full_path'],
                                  project_fixture['project_name'],
                                  ['subdir1'],
                                  'test2')
        page_object.new_page_object(test_directory_fixture['full_path'],
                                  project_fixture['project_name'],
                                  [],
                                  'test1')
        pages = utils.get_pages(test_directory_fixture['full_path'],
                                       project_fixture['project_name'])

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

    def test_get_suites(self, test_directory_fixture, project_fixture):
        suite.new_suite(test_directory_fixture['full_path'],
                        project_fixture['project_name'],
                        'suite1')
        suite.new_suite(test_directory_fixture['full_path'],
                        project_fixture['project_name'],
                        'suite2')
        
        suites = utils.get_suites(test_directory_fixture['full_path'],
                                  project_fixture['project_name'])
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

    def test_get_projects(self, project_fixture):
        projects = utils.get_projects(project_fixture['test_directory_fixture']['full_path'])
        assert project_fixture['project_name'] in projects


class Test_get_files_in_directory_dot_path:

    def test_get_files_in_directory_dot_path(self, project_fixture, test_directory_fixture):
        # create a new page object in pages folder
        page_object.new_page_object(test_directory_fixture['full_path'],
                                    project_fixture['project_name'],
                                    [],
                                    'page1')
        # create a new page object in pages/dir/subdir/
        page_object.new_page_object(test_directory_fixture['full_path'],
                                    project_fixture['project_name'],
                                    ['dir', 'subdir'],
                                    'page2')
        base_path = os.path.join(test_directory_fixture['full_path'],
                                 'projects',
                                 project_fixture['project_name'],
                                 'pages')
        dotted_files = utils.get_files_in_directory_dot_path(base_path)
        assert 'page1' in dotted_files
        assert 'dir.subdir.page2' in dotted_files
        assert len(dotted_files) == 2


