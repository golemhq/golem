import os
import sys

import pytest

from golem.core import page
from golem.core.page import Page
from golem.core.project import Project


class TestCreatePage:

    def test_create_page(self, project_session, test_utils):
        _, project = project_session.activate()
        page_name = test_utils.random_string()
        page.create_page(project, page_name)
        assert page_name in Project(project).pages()

    def test_create_page_page_exists(self, project_session, test_utils):
        _, project = project_session.activate()
        page_name = test_utils.random_string()
        page.create_page(project, page_name)
        errors = page.create_page(project, page_name)
        assert errors == ['A page with that name already exists']

    def test_create_page_into_subdirectory(self, project_session, test_utils):
        _, project = project_session.activate()
        random_dir = test_utils.random_string()
        page_name = '{}.page_name'.format(random_dir)
        page.create_page(project, page_name)
        init_path = os.path.join(Project(project).page_directory_path,
                                 random_dir, '__init__.py')
        assert os.path.isfile(init_path)

    def test_create_page_invalid_name(self, project_session):
        _, project = project_session.activate()
        errors = page.create_page(project, 'invalid-name')
        assert errors == ['Only letters, numbers and underscores are allowed']
        errors = page.create_page(project, 'test.')
        assert errors == ['File name cannot be empty']
        errors = page.create_page(project, '.test')
        assert errors == ['Directory name cannot be empty']


class TestRenamePage:

    def test_rename_page(self, project_session, test_utils):
        _, project = project_session.activate()
        page_name = test_utils.create_random_page(project)
        new_page_name = test_utils.random_string()
        page.rename_page(project, page_name, new_page_name)
        pages = Project(project).pages()
        assert page_name not in pages
        assert new_page_name in pages

    def test_rename_page_to_new_directory(self, project_session, test_utils):
        _, project = project_session.activate()
        page_name = test_utils.create_random_page(project)
        random_dirname = test_utils.random_string()
        new_page_name = '{}.{}'.format(random_dirname, test_utils.random_string())
        errors = page.rename_page(project, page_name, new_page_name)
        assert errors == []
        pages = Project(project).pages()
        assert page_name not in pages
        assert new_page_name in pages
        init_file_path = os.path.join(Project(project).page_directory_path,
                                      random_dirname, '__init__.py')
        assert os.path.isfile(init_file_path)

    def test_rename_page_invalid_name(self, project_session, test_utils):
        _, project = project_session.activate()
        page_name = test_utils.create_random_page(project)
        errors = page.rename_page(project, page_name, 'invalid-name')
        assert errors == ['Only letters, numbers and underscores are allowed']
        errors = page.rename_page(project, page_name, 'page.')
        assert errors == ['File name cannot be empty']
        errors = page.rename_page(project, page_name, '.page')
        assert errors == ['Directory name cannot be empty']


class TestDuplicatePage:

    def test_duplicate_page(self, project_session, test_utils):
        _, project = project_session.activate()
        page_name = test_utils.create_random_page(project)
        new_page_name = test_utils.random_string()
        errors = page.duplicate_page(project, page_name, new_page_name)
        assert errors == []
        pages = Project(project).pages()
        assert page_name in pages
        assert new_page_name in pages

    def test_duplicate_page_same_name(self, project_session, test_utils):
        _, project = project_session.activate()
        page_name = test_utils.create_random_page(project)
        errors = page.duplicate_page(project, page_name, page_name)
        assert errors == ['New page name cannot be the same as the original']

    def test_duplicate_page_name_already_exists(self, project_session, test_utils):
        _, project = project_session.activate()
        page_name = test_utils.create_random_page(project)
        page_name_two = test_utils.create_random_page(project)
        errors = page.duplicate_page(project, page_name, page_name_two)
        assert errors == ['A page with that name already exists']

    def test_duplicate_page_invalid_name(self, project_session, test_utils):
        _, project = project_session.activate()
        page_name = test_utils.create_random_page(project)
        errors = page.duplicate_page(project, page_name, 'new-name')
        assert errors == ['Only letters, numbers and underscores are allowed']
        errors = page.duplicate_page(project, page_name, 'page.')
        assert errors == ['File name cannot be empty']
        errors = page.duplicate_page(project, page_name, '.page')
        assert errors == ['Directory name cannot be empty']


class TestEditPage:

    def test_edit_page(self, project_session, test_utils):
        _, project = project_session.activate()
        page_name = test_utils.create_random_page(project)
        elements = [
            {'name': 'a', 'selector': 'id', 'value': 'b', 'display_name': 'a'},
            {'name': 'c', 'selector': 'id', 'value': 'd', 'display_name': ''}
        ]
        functions = ["def func1(a, b):\n    print(a, b)\n"]
        import_lines = [
            'import time',
            'from golem import browser'
        ]
        page.edit_page(project, page_name, elements, functions, import_lines)
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
        with open(Page(project, page_name).path) as f:
            assert f.read() == expected_contents

    element_values = [
        ("'abc'", "abc"),
        ('"abc"', 'abc'),
        ('"""abc"""', 'abc')
    ]

    @pytest.mark.parametrize('value,expected_value', element_values)
    def test_edit_page_selector_value_format(self, value, expected_value,
                                             project_session, test_utils):
        _, project = project_session.activate()
        page_name = test_utils.create_random_page(project)
        elements = [
            {'name': 'foo', 'selector': 'id', 'value': value, 'display_name': 'foo'},
        ]
        page.edit_page(project, page_name, elements, [], [])
        elements = Page(project, page_name).components['elements']
        assert elements[0]['value'] == expected_value


class TestEditPageCode:

    def test_edit_page_code(self, project_session, test_utils):
        _, project = project_session.activate()
        page_name = test_utils.create_random_page(project)
        page_code = ("elem1 = ('id', 'x')\n"
                     "elem2 = ('id', 'y')\n"
                     "def func1():\n"
                     "   pass")
        page.edit_page_code(project, page_name, page_code)
        with open(Page(project, page_name).path) as f:
            assert f.read() == page_code


class TestDeletePage:

    def test_delete_page(self, project_session, test_utils):
        _, project = project_session.activate()
        page_name = test_utils.create_random_page(project)
        errors = page.delete_page(project, page_name)
        assert errors == []
        assert page_name not in Project(project).pages()
        assert not os.path.isfile(Page(project, page_name).path)

    def test_delete_page_not_exist(self, project_session):
        _, project = project_session.activate()
        errors = page.delete_page(project, 'not-exist')
        assert errors == ['Page not-exist does not exist']


class TestPagePath:

    def test_page_path(self, project_session, test_utils):
        testdir, project = project_session.activate()
        page_one = test_utils.random_string()
        random_dir = test_utils.random_string()
        random_name = test_utils.random_string()
        page_two = '{}.{}'.format(random_dir, random_name)
        test_utils.create_page(project, page_one)
        test_utils.create_page(project, page_two)
        path_one = os.path.join(Project(project).page_directory_path, page_one + '.py')
        path_two = os.path.join(Project(project).page_directory_path,
                                random_dir, random_name + '.py')
        assert Page(project, page_one).path == path_one
        assert Page(project, page_two).path == path_two


class TestPageExists:

    def test_page_exists(self, project_session, test_utils):
        _, project = project_session.activate()
        page_name = test_utils.create_random_page(project)
        assert Page(project, page_name).exists
        assert not Page(project, 'not_exists_page').exists


class TestPageCode:

    def test_page_code(self, project_session, test_utils):
        _, project = project_session.activate()
        page_name = test_utils.create_random_page(project)
        file_content = 'test=("id", "xyz")\ntest2=("id", "abc")\n'
        page.edit_page_code(project, page_name, file_content)
        assert Page(project, page_name).code == file_content

    def test_get_page_code_file_not_exist(self, project_session):
        _, project = project_session.activate()
        assert Page(project, 'does-not-exist').code is None


class TestPageComponents:

    def test_page_components(self, project_session, test_utils):
        _, project = project_session.activate()
        page_name = test_utils.create_random_page(project)
        page_obj = Page(project, page_name)
        with open(page_obj.path, 'w') as f:
            f.write('elem1 = (\'id\', \'someId\', \'Elem1\')\n')
            f.write('def func1(c, b, a):\n')
            f.write('    pass\n')
        components = page_obj.components
        expected = {
            'functions': [
                {
                    'name': 'func1',
                    'full_name': '{}.func1'.format(page_name),
                    'partial_name': '{}.func1'.format(page_name),
                    'description': None,
                    'arguments': ['c', 'b', 'a'],
                    'code': 'def func1(c, b, a):\n    pass\n'
                }
            ],
            'elements': [
                {
                    'name': 'elem1',
                    'selector': 'id',
                    'value': 'someId',
                    'display_name': 'Elem1',
                    'partial_name': '{}.elem1'.format(page_name),
                    'full_name': '{}.elem1'.format(page_name)
                }
            ],
            'import_lines': [],
            'code_lines': ["elem1 = ('id', 'someId', 'Elem1')",
                           'def func1(c, b, a):',
                           '    pass',
                           ''],
            'source_code': ("elem1 = ('id', 'someId', 'Elem1')\ndef func1(c, b, a):\n"
                            "    pass\n")
        }
        assert components == expected

    def test_page_components_import_lines(self, project_session, test_utils):
        _, project = project_session.activate()
        page_name = test_utils.create_random_page(project)
        code = ('import foo\n'
                'import bar\n'
                'from bar import baz\n'
                'from golem.browser import InvalidBrowserIdError, open_browser\n'
                'from module import (func1,\n'
                '                    func2)\n'
                '\n'
                'element_one = ("id", "idX", "Element One")\n'
                'element_two = ("id", "idX .import", "Element Two")\n'
                'element_three = ("id", "idX .from .import", "Element Three")\n')
        page.edit_page_code(project, page_name, code)
        components = Page(project, page_name).components
        expected = [
            'import foo',
            'import bar',
            'from bar import baz',
            'from golem.browser import InvalidBrowserIdError, open_browser',
            'from module import (func1,\n                    func2)'
        ]
        assert sorted(components['import_lines']) == sorted(expected)

    def test_page_components_imported_names(self, project_session, test_utils):
        """Elements and functions from imported modules are not returned
        as components of a page
        """
        testdir, project = project_session.activate()
        sys.path.append(testdir)
        page_one = test_utils.create_random_page(project)
        code = ('elem1 = ("id", "test")\n'
                '\n'
                'def func1():\n'
                '    pass\n')
        page.edit_page_code(project, page_one, code)

        # page_two imports page_one
        page_two = test_utils.create_random_page(project)
        code = ('from projects.{}.pages import {}\n'
                '\n'
                'elem2 = ("id", "test")\n'
                '\n'
                'def func2():\n'
                '    pass\n'.format(project, page_one))
        page.edit_page_code(project, page_two, code)
        components = Page(project, page_two).components
        assert len(components['elements']) == 1
        assert components['elements'][0]['name'] == 'elem2'
        assert len(components['functions']) == 1
        assert components['functions'][0]['name'] == 'func2'

        # import *
        code = ('from projects.{}.pages.{} import *\n'
                '\n'
                'elem3 = ("id", "test")\n'
                '\n'
                'def func3():\n'
                '    pass\n'.format(project, page_one))
        page.edit_page_code(project, page_two, code)
        components = Page(project, page_two).components
        assert len(components['elements']) == 1
        assert components['elements'][0]['name'] == 'elem3'
        assert len(components['functions']) == 1
        assert components['functions'][0]['name'] == 'func3'

    def test_page_components_nested_import(self, project_session, test_utils):
        """Elements and functions from imported modules are not returned
        as components of a page
        """
        testdir, project = project_session.activate()
        sys.path.append(testdir)
        page_one = test_utils.create_random_page(project)
        code = 'elem1 = ("id", "test")\n'
        page.edit_page_code(project, page_one, code)

        # page_two imports page_one
        page_two = test_utils.create_random_page(project)
        code = ('from projects.{}.pages import {}\n'
                '\n'
                'elem2 = ("id", "test")\n'.format(project, page_one))
        page.edit_page_code(project, page_two, code)

        # page_three imports page_two
        page_three = test_utils.create_random_page(project)
        code = ('from projects.{}.pages import {}\n'
                '\n'
                'elem3 = ("id", "test")\n'.format(project, page_two))
        page.edit_page_code(project, page_three, code)
        components = Page(project, page_three).components
        assert len(components['elements']) == 1
        assert components['elements'][0]['name'] == 'elem3'

        # import *
        code = ('from projects.{}.pages.{} import *\n'
                '\n'
                'elem3 = ("id", "test")\n'.format(project, page_two))
        page.edit_page_code(project, page_three, code)
        components = Page(project, page_three).components
        assert len(components['elements']) == 1
        assert components['elements'][0]['name'] == 'elem3'
