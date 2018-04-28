import os
import types
import inspect
from collections import OrderedDict
from subprocess import call

import pytest

from golem.core import utils, page_object, test_case, suite

from tests.fixtures import project_class, testdir_session, dir_function
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


class Test_validate_python_file_syntax:
    
    def test_syntax_correct(self, dir_function):
        filename = 'test_python_syntax.py'
        filepath = os.path.join(dir_function['path'], filename)
        filecontent = ('import os\n'
                       'var = 2 + 2\n'
                       'print(var)\n'
                       'def func():\n'
                       '    pass\n')
        with open(filepath, 'w') as f:
            f.write(filecontent)
        error = utils.validate_python_file_syntax(filepath)
        assert error == ''


    syntax_tests = [
        (
            ('var = 2 +\n'),
            ('    var = 2 +\n'
             '            ^\n'
             'SyntaxError: invalid syntax\n')
        ),
        (
            ('import\n'
             'var = 2 + 2'),
            ('    import\n'
             '         ^\n'
             'SyntaxError: invalid syntax\n')
        ),
        (
            ('def func()\n'
             '    var = 2 + 2\n'),
            ('    def func()\n'
             '             ^\n'
             'SyntaxError: invalid syntax\n')
        ),
    ]

    @pytest.mark.parametrize('filecontent,expected', syntax_tests)
    def test_incorrect_syntax(self, filecontent, expected, dir_function):
        filename = 'test_python_syntax.py'
        filepath = os.path.join(dir_function['path'], filename)
        with open(filepath, 'w') as f:
            f.write(filecontent)
        error = utils.validate_python_file_syntax(filepath)
        print(error)
        assert expected in error


class Test_import_module:

    def test_import_module(self, dir_function):
        filename = 'python_module.py'
        filepath = os.path.join(dir_function['path'], filename)
        filecontent = ('foo = 2\n'
                       'def bar(a, b):\n'
                       '    baz = ""\n')
        with open(filepath, 'w') as f:
            f.write(filecontent)
        module = utils.import_module(filepath)
        assert type(module) == types.ModuleType
        
        foo = getattr(module, 'foo')
        assert type(foo) == int

        bar = getattr(module, 'bar')
        assert type(bar) == types.FunctionType

        args = list(inspect.signature(bar).parameters)
        code = inspect.getsource(bar)
        assert args == ['a', 'b']
        assert code == 'def bar(a, b):\n    baz = ""\n'


    def test_module_does_not_exist(self, dir_function):
        filepath = os.path.join(dir_function['path'], 'non_existent.py')
        module = utils.import_module(filepath)
        assert module == None
