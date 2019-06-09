import os

from golem.core import test_case, page_object, suite
from golem.core.project import Project, create_project


class TestCreateProject:

    def test_create_project(self, testdir_session, test_utils):
        testdir_session.activate()
        project_name = test_utils.random_string(5)
        create_project(project_name)
        path = Project(project_name).path
        listdir = os.listdir(path)
        files = [n for n in listdir if os.path.isfile(os.path.join(path, n))]
        dirs = [n for n in listdir if os.path.isdir(os.path.join(path, n))]
        if '.DS_Store' in files:
            files.remove('.DS_Store')
        assert len(files) == 5
        # verify files
        assert '__init__.py' in files
        assert 'extend.py' in files
        assert 'environments.json' in files
        assert 'settings.json' in files
        assert 'secrets.json' in files
        # verify directories
        assert len(dirs) == 4
        # verify the test dir contains the correct directories
        assert 'pages' in dirs
        assert 'reports' in dirs
        assert 'tests' in dirs
        assert 'suites' in dirs


class TestTestTree:

    def test_test_tree(self, project_function):
        _, project = project_function.activate()
        test_case.new_test_case(project, ['subdir1', 'subdir2'], 'test3')
        test_case.new_test_case(project, ['subdir1'], 'test2')
        test_case.new_test_case(project, [], 'test1')
        tests = Project(project).test_tree
        expected = {
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
        assert tests == expected

    def test_test_tree_no_tests(self, project_function):
        _, project = project_function.activate()
        tests = Project(project).test_tree
        expected = {'type': 'directory', 'name': 'tests', 'dot_path': '.', 'sub_elements': []}
        assert tests == expected


class TestPageTree:

    def test_page_tree(self, project_function):
        _, project = project_function.activate()
        page_object.new_page_object(project, ['subdir1', 'subdir2'], 'test3')
        page_object.new_page_object(project, ['subdir1'], 'test2')
        page_object.new_page_object(project, [], 'test1')
        pages = Project(project).page_tree
        expected = {
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
        assert pages == expected

    def test_page_tree_no_pages(self, project_function):
        _, project = project_function.activate()
        pages = Project(project).page_tree
        expected = {'type': 'directory', 'name': 'pages', 'dot_path': '.', 'sub_elements': []}
        assert pages == expected


class TestSuiteTree:

    def test_suite_tree(self, project_function):
        _, project = project_function.activate()
        suite.new_suite(project, [], 'suite1')
        suite.new_suite(project, [], 'suite2')
        suites = Project(project).suite_tree
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

    def test_suite_tree_no_suites(self, project_function):
        _, project = project_function.activate()
        suites = Project(project).suite_tree
        expected = {'type': 'directory', 'name': 'suites', 'dot_path': '.', 'sub_elements': []}
        assert suites == expected


class TestGetTests:

    def test_get_tests(self, project_function, test_utils):
        _, project_name = project_function.activate()
        test_utils.create_test(project_name, [''], 'test_one')
        test_utils.create_test(project_name, ['foo'], 'test_two')
        test_utils.create_test(project_name, ['foo', 'bar'], 'test_three')
        test_utils.create_test(project_name, ['foo', 'bar', 'baz'], 'test_four')
        project = Project(project_name)
        tests = project.tests()
        expected = ['test_one', 'foo.test_two', 'foo.bar.test_three', 'foo.bar.baz.test_four']
        assert tests == expected
        tests = project.tests('foo')
        expected = ['foo.test_two', 'foo.bar.test_three', 'foo.bar.baz.test_four']
        assert tests == expected
        tests = project.tests('foo/')
        assert tests == expected
        expected = ['foo.bar.test_three', 'foo.bar.baz.test_four']
        tests = project.tests('foo/bar')
        assert tests == expected


class TestHasTests:

    def test_project_has_tests(self, project_function, test_utils):
        _, project = project_function.activate()
        assert not Project(project).has_tests
        test_utils.create_test(project, [], 'test01')
        assert Project(project).has_tests
