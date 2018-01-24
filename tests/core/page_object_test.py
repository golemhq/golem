import os
import sys

from golem.core import page_object

from tests.fixtures import (testdir_fixture,
                            random_project_fixture,
                            permanent_project_fixture)
from tests import helper_functions


class Test_page_exists:

    def test_page_exists(self, permanent_project_fixture):
        project = permanent_project_fixture['name']
        testdir = permanent_project_fixture['testdir']
        page_object.new_page_object(testdir, project, [], 'page_x001_exist')
        exists = page_object.page_exists(testdir, project, 'page_x001_exist')
        not_exists = page_object.page_exists(testdir, project, 'page_x001_not_exist')
        assert exists
        assert not not_exists


class Test_get_page_object_content:

    def test_get_page_object_content(self, permanent_project_fixture):
        project = permanent_project_fixture['name']
        testdir = permanent_project_fixture['testdir']
        page_name = 'page_test_get_content_ab1412'

        page_object.new_page_object(testdir, project, [],
                                    page_name, add_parents=False)
        page_path = os.path.join(testdir, 'projects',
                                 project, 'pages', page_name + '.py')
        with open(page_path, 'w') as page_file:
            page_file.write('elem1 = (\'id\', \'someId\', \'Elem1\')\n')
            page_file.write('def func1(c, b, a):\n')
            page_file.write('    pass')

        content = page_object.get_page_object_content(project, page_name)

        expected = {
            'functions': [
                {
                    'function_name': 'func1',
                    'full_function_name': 'page_test_get_content_ab1412.func1',
                    'description': None,
                    'arguments': ['c', 'b', 'a'],
                    'code': 'def func1(c, b, a):\n    pass\n'
                }],
            'elements': [
                {
                    'element_name': 'elem1',
                    'element_selector': 'id',
                    'element_value': 'someId',
                    'element_display_name': 'Elem1',
                    'element_full_name': 'page_test_get_content_ab1412.elem1'
                }],
            'import_lines': [],
            'code_lines': ["elem1 = ('id', 'someId', 'Elem1')",
                           'def func1(c, b, a):',
                           '    pass',
                           ''],
            'source_code': ("elem1 = ('id', 'someId', 'Elem1')\ndef func1(c, b, a):\n"
                            "    pass\n")
        }
        assert content == expected


class Test_get_page_object_code:

    def test_get_page_object_code(self, permanent_project_fixture):
        project = permanent_project_fixture['name']
        testdir = permanent_project_fixture['testdir']
        page_name = 'page_test_get_code_ab8456'

        page_object.new_page_object(testdir, project, [],
                                    page_name, add_parents=False)
        page_path = os.path.join(testdir, 'projects',
                                 project, 'pages', page_name + '.py')
        file_content = 'test=("id", "xyz")\ntest2=("id", "abc")\n'
        with open(page_path, 'w') as page_file:
            page_file.write(file_content)
        code = page_object.get_page_object_code(page_path)
        assert code == file_content


    def test_get_page_object_code_file_not_exist(self, permanent_project_fixture):
        project = permanent_project_fixture['name']
        testdir = permanent_project_fixture['testdir']
        page_path = os.path.join(testdir, 'projects',
                                 project, 'pages', 'does', 'not', 'exist54654.py')
        code = page_object.get_page_object_code(page_path)
        assert code == ''


class Test_save_page_object:

    def test_save_page_object(self, permanent_project_fixture):
        project = permanent_project_fixture['name']
        testdir = permanent_project_fixture['testdir']
        page_path = os.path.join(testdir, 'projects', project,
                                 'pages', 'testa', 'testb',
                                 'page_test987.py')
        page_object.new_page_object(testdir, project, ['testa', 'testb'],
                                    'page_test987', add_parents=True)
        page_name = 'testa.testb.page_test987'
        elements = [
            {'name': 'a', 'selector': 'id', 'value': 'b', 'display_name': 'a'},
            {'name': 'c', 'selector': 'id', 'value': 'd', 'display_name': ''}
        ]
        functions = ["def func1(a, b):\n    print(a, b)\n"]
        import_lines = [
            'import time',
            'from golem import browser'
        ]
        page_object.save_page_object(testdir, project, page_name,
                                     elements, functions, import_lines)
        expected_contents = ('import time\n'
                             'from golem import browser\n'
                             '\n'
                             '\n'
                             'a = (\'id\', \'b\', \'a\')\n'
                             '\n'
                             'c = (\'id\', \'d\', \'c\')\n'
                             '\n'
                             'def func1(a, b):\n'
                             '    print(a, b)\n')
        with open(page_path) as page_file:
            contents = page_file.read()
            assert contents == expected_contents