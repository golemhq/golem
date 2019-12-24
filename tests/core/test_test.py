import os
import sys

import pytest

from golem.core import test as test_module, settings_manager
from golem.core.project import Project
from golem.core.test import Test


SAMPLE_TEST_CONTENT = """
description = 'some description'

tags = []

data = [{'a': 'b'}]

pages = ['page1', 'page2']

def setup(data):
    page1.func1()

def test(data):
    page2.func2('a', 'b')
    click(page2.elem1)

def teardown(data):
    pass

"""


NEW_TEST_CONTENT = """
description = ''

tags = []

pages = []


def setup(data):
    pass


def test(data):
    pass


def teardown(data):
    pass

"""


EMPTY_STEPS = {'setup': [], 'test': [], 'teardown': []}


class TestCreateTest:

    def test_create_test(self, project_session, test_utils):
        _, project = project_session.activate()
        test_name = test_utils.random_string()
        errors = test_module.create_test(project, test_name)
        test = Test(project, test_name)
        assert test.exists
        assert errors == []
        assert test.code == NEW_TEST_CONTENT

    def test_create_test_name_exists(self, project_session, test_utils):
        _, project = project_session.activate()
        test_name = test_utils.random_string()
        test_module.create_test(project, test_name)
        errors = test_module.create_test(project, test_name)
        assert errors == ['A test with that name already exists']

    def test_create_test_invalid_name(self, project_session):
        _, project = project_session.activate()
        # invalid chars
        invalid_names = [
            'te-st',
            'te st',
            'te?st',
            'test. .test'
        ]
        for name in invalid_names:
            errors = test_module.create_test(project, name)
            assert errors == ['Only letters, numbers and underscores are allowed']
        # empty directory
        invalid_names = [
            '.test',
            'test..test',
        ]
        for name in invalid_names:
            errors = test_module.create_test(project, name)
            assert errors == ['Directory name cannot be empty']
        # empty file name
        invalid_names = [
            '',
            'test.',
        ]
        for name in invalid_names:
            errors = test_module.create_test(project, name)
            assert errors == ['File name cannot be empty']

    def test_create_test_into_folder(self, project_session, test_utils):
        _, project = project_session.activate()
        random_dir = test_utils.random_string()
        # to folder
        test_name = '{}.test001'.format(random_dir)
        errors = test_module.create_test(project, test_name)
        assert errors == []
        # verify that each parent dir has __init__.py file
        init_path = os.path.join(Project(project).test_directory_path,
                                 random_dir, '__init__.py')
        assert test_name in Project(project).tests()
        assert os.path.isfile(init_path)
        # to sub-folder
        random_dir = test_utils.random_string()
        random_subdir = test_utils.random_string()
        test_name = '{}.{}.test001'.format(random_dir, random_subdir)
        errors = test_module.create_test(project, test_name)
        assert errors == []
        assert test_name in Project(project).tests()
        # verify that each parent dir has __init__.py file
        init_path = os.path.join(Project(project).test_directory_path,
                                 random_dir, '__init__.py')
        assert os.path.isfile(init_path)
        init_path = os.path.join(Project(project).test_directory_path,
                                 random_dir, random_subdir, '__init__.py')
        assert os.path.isfile(init_path)


class TestRenameTest:

    def test_rename_test(self, project_session, test_utils):
        _, project = project_session.activate()
        test_name = test_utils.create_random_test(project)
        new_test_name = test_utils.random_string()
        errors = test_module.rename_test(project, test_name, new_test_name)
        assert errors == []
        tests = Project(project).tests()
        assert test_name not in tests
        assert new_test_name in tests

    def test_rename_test_in_folder(self, project_session, test_utils):
        _, project = project_session.activate()
        dir = test_utils.random_string()
        name = test_utils.random_string()
        test_name = '{}.{}'.format(dir, name)
        test_utils.create_test(project, test_name)
        # rename within same folder
        new_name = test_utils.random_string()
        new_test_name = '{}.{}'.format(dir, new_name)
        errors = test_module.rename_test(project, test_name, new_test_name)
        assert errors == []
        tests = Project(project).tests()
        assert test_name not in tests
        assert new_test_name in tests
        # rename to another non existent folder
        test_name = new_test_name
        name = new_name
        new_dir = test_utils.random_string()
        new_test_name = '{}.{}'.format(new_dir, name)
        errors = test_module.rename_test(project, test_name, new_test_name)
        assert errors == []
        tests = Project(project).tests()
        assert test_name not in tests
        assert new_test_name in tests

    def test_rename_test_invalid_name(self, project_session, test_utils):
        _, project = project_session.activate()
        test_name = test_utils.create_random_test(project)
        # invalid chars
        new_test_name = 'new-name'
        errors = test_module.rename_test(project, test_name, new_test_name)
        assert errors == ['Only letters, numbers and underscores are allowed']
        tests = Project(project).tests()
        assert test_name in tests
        assert new_test_name not in tests
        # empty filename
        new_test_name = 'test.'
        errors = test_module.rename_test(project, test_name, new_test_name)
        assert errors == ['File name cannot be empty']
        tests = Project(project).tests()
        assert test_name in tests
        assert new_test_name not in tests
        # empty directory
        new_test_name = 'test..test'
        errors = test_module.rename_test(project, test_name, new_test_name)
        assert errors == ['Directory name cannot be empty']
        tests = Project(project).tests()
        assert test_name in tests
        assert new_test_name not in tests

    def test_rename_test_src_does_not_exist(self, project_session, test_utils):
        _, project = project_session.activate()
        test_name = test_utils.random_string()
        new_test_name = test_utils.random_string()
        errors = test_module.rename_test(project, test_name, new_test_name)
        assert errors == ['Test {} does not exist'.format(test_name)]
        assert new_test_name not in Project(project).tests()

    def test_rename_test_with_data_file(self, project_session, test_utils):
        """Assert when a test has a data file the data file is renamed as well"""
        _, project = project_session.activate()
        test_name = test_utils.create_random_test(project)
        new_test_name = test_utils.random_string()
        data_path = os.path.splitext(Test(project, test_name).path)[0] + '.csv'
        with open(data_path, 'w+') as f:
            f.write('')
        new_data_path = os.path.splitext(Test(project, new_test_name).path)[0] + '.csv'
        test_module.rename_test(project, test_name, new_test_name)
        assert not os.path.isfile(data_path)
        assert os.path.isfile(new_data_path)

    def test_rename_dest_exists(self, project_session, test_utils):
        _, project = project_session.activate()
        dir = test_utils.random_string()
        name_one = test_utils.random_string()
        test_one = '{}.{}'.format(dir, name_one)
        name_two = test_utils.random_string()
        test_two = '{}.{}'.format(dir, name_two)
        test_utils.create_test(project, test_one)
        test_utils.create_test(project, test_two)
        # rename test to existing test name
        errors = test_module.rename_test(project, test_one, test_two)
        assert errors == ['A file with that name already exists']
        # rename test to same name
        errors = test_module.rename_test(project, test_one, test_one)
        assert errors == ['A file with that name already exists']

    @pytest.mark.skipif("os.name != 'nt'")
    def test_rename_test_test_is_open(self, project_session, test_utils):
        """Try to rename a test while it is open"""
        _, project = project_session.activate()
        test_name = test_utils.create_random_test(project)
        new_test_name = test_utils.random_string()
        with open(Test(project, test_name).path) as f:
            errors = test_module.rename_test(project, test_name, new_test_name)
            assert errors == ['There was an error renaming file']


class TestDuplicateTest:

    def test_duplicate_test(self, project_session, test_utils):
        _, project = project_session.activate()
        # in root folder
        test_name = test_utils.create_random_test(project)
        new_test_name = test_utils.random_string()
        errors = test_module.duplicate_test(project, test_name, new_test_name)
        assert errors == []
        tests = Project(project).tests()
        assert test_name in tests
        assert new_test_name in tests
        # in folder
        dir = test_utils.random_string()
        name = test_utils.random_string()
        test_name = '{}.{}'.format(dir, name)
        test_utils.create_test(project, test_name)
        new_name = test_utils.random_string()
        new_test_name = '{}.{}'.format(dir, new_name)
        errors = test_module.duplicate_test(project, test_name, new_test_name)
        assert errors == []
        tests = Project(project).tests()
        assert test_name in tests
        assert new_test_name in tests

    def test_duplicate_test_same_name(self, project_session, test_utils):
        _, project = project_session.activate()
        test_name = test_utils.create_random_test(project)
        errors = test_module.duplicate_test(project, test_name, test_name)
        assert errors == ['New test name cannot be the same as the original']

    def test_duplicate_test_dest_exists(self, project_session, test_utils):
        _, project = project_session.activate()
        test_one = test_utils.create_random_test(project)
        test_two = test_utils.create_random_test(project)
        errors = test_module.duplicate_test(project, test_one, test_two)
        assert errors == ['A test with that name already exists']
        # to another folder
        test_one = test_utils.create_random_test(project)
        test_two = '{}.{}'.format(test_utils.random_string(), test_utils.random_string())
        test_utils.create_test(project, test_two)
        errors = test_module.duplicate_test(project, test_one, test_two)
        assert errors == ['A test with that name already exists']
        # to same name
        test_one = test_utils.create_random_test(project)
        test_utils.create_test(project, test_two)
        errors = test_module.duplicate_test(project, test_one, test_one)
        assert errors == ['New test name cannot be the same as the original']

    def test_duplicate_test_invalid_name(self, project_session, test_utils):
        _, project = project_session.activate()
        test_name = test_utils.create_random_test(project)
        # invalid name
        new_test_name = 'new-name'
        errors = test_module.duplicate_test(project, test_name, new_test_name)
        assert errors == ['Only letters, numbers and underscores are allowed']
        # empty name
        new_test_name = 'test.'
        errors = test_module.duplicate_test(project, test_name, new_test_name)
        assert errors == ['File name cannot be empty']
        # empty directory
        new_test_name = 'test.'
        errors = test_module.duplicate_test(project, test_name, new_test_name)
        assert errors == ['File name cannot be empty']

    def test_duplicate_test_with_data_file(self, project_session, test_utils):
        """Assert when a test has a data file the data file is duplicated as well"""
        _, project = project_session.activate()
        test_name = test_utils.create_random_test(project)
        new_test_name = test_utils.random_string()
        data_path = os.path.splitext(Test(project, test_name).path)[0] + '.csv'
        with open(data_path, 'w+') as f:
            f.write('')
        new_data_path = os.path.splitext(test_module.Test(project, new_test_name).path)[0] + '.csv'
        test_module.duplicate_test(project, test_name, new_test_name)
        assert os.path.isfile(data_path)
        assert os.path.isfile(new_data_path)


class TestEditTest:

    def test_edit_test_data_infile(self, project_function, test_utils):
        _, project = project_function.activate()
        test_name = test_utils.create_random_test(project)
        description = 'description'
        pages = ['page1', 'page2']
        test_steps = {
            'setup': [
                {'type': 'function-call', 'action': 'click', 'parameters': ['elem1']}
            ],
            'test': [
                {'type': 'function-call', 'action': 'send_keys', 'parameters': ['elem2', 'keys']}
            ],
            'teardown': []
        }
        data = [{
            'key': '\'value\''
        }]
        settings_manager.save_project_settings(project, '{"test_data": "infile"}')
        test_module.edit_test(project, test_name, description, pages, test_steps, data, [])
        expected = (
            '\n'
            'description = \'description\'\n'
            '\n'
            'tags = []\n'
            '\n'
            'pages = [\'page1\',\n'
            '         \'page2\']\n'
            '\n'
            'data = [\n'
            '    {\n'
            '        \'key\': \'value\',\n'
            '    },\n'
            ']\n'
            '\n\n'
            'def setup(data):\n'
            '    click(elem1)\n'
            '\n\n'
            'def test(data):\n'
            '    send_keys(elem2, keys)\n'
            '\n\n'
            'def teardown(data):\n'
            '    pass\n')
        with open(Test(project, test_name).path) as f:
            assert f.read() == expected

    def test_edit_test_data_csv(self, project_function, test_utils):
        _, project = project_function.activate()
        test_name = test_utils.create_random_test(project)
        description = 'description'
        pages = []
        test_steps = {
            'setup': [],
            'test': [
                {'type': 'function-call', 'action': 'send_keys', 'parameters': ['elem2', 'keys']}
            ],
            'teardown': []
        }
        data = [{
            'key': '\'value\''
        }]
        settings_manager.save_project_settings(project, '{"test_data": "csv"}')
        test_module.edit_test(project, test_name, description, pages, test_steps, data, [])
        expected = (
            '\n'
            'description = \'description\'\n'
            '\n'
            'tags = []\n'
            '\n'
            'pages = []\n'
            '\n\n'
            'def setup(data):\n'
            '    pass\n'
            '\n\n'
            'def test(data):\n'
            '    send_keys(elem2, keys)\n'
            '\n\n'
            'def teardown(data):\n'
            '    pass\n')
        with open(Test(project, test_name).path) as f:
            assert f.read() == expected
        data_path = os.path.join(Project(project).test_directory_path,
                                 '{}.csv'.format(test_name))
        expected = ('key\n'
                    '\'value\'\n')
        with open(data_path) as f:
            assert f.read() == expected

    def test_edit_test_explicit_page_import(self, project_function, test_utils):
        _, project = project_function.activate()
        test_name = test_utils.create_random_test(project)
        pages = ['page1', 'module.page2']
        settings_manager.save_project_settings(project, '{"implicit_page_import": false}')
        test_module.edit_test(project, test_name, description='', pages=pages,
                              steps=EMPTY_STEPS, test_data=[], tags=[])
        expected = ('from projects.{}.pages import page1\n'
                    'from projects.{}.pages.module import page2\n'
                    '\n\n'
                    'description = \'\'\n'
                    '\n'
                    'tags = []\n'
                    '\n\n'
                    'def setup(data):\n'
                    '    pass\n'
                    '\n\n'
                    'def test(data):\n'
                    '    pass\n'
                    '\n\n'
                    'def teardown(data):\n'
                    '    pass\n'.format(project, project))
        with open(Test(project, test_name).path) as f:
            assert f.read() == expected

    def test_edit_test_explicit_action_import(self, project_function, test_utils):
        _, project = project_function.activate()
        test_name = test_utils.create_random_test(project)
        settings_manager.save_project_settings(project, '{"implicit_actions_import": false}')
        test_module.edit_test(project, test_name, description='', pages=[],
                              steps=EMPTY_STEPS, test_data=[], tags=[])
        expected = ('from golem import actions\n\n\n'
                    'description = \'\'\n\n'
                    'tags = []\n\n'
                    'pages = []\n\n\n'
                    'def setup(data):\n'
                    '    pass\n\n\n'
                    'def test(data):\n'
                    '    pass\n\n\n'
                    'def teardown(data):\n'
                    '    pass\n')
        with open(Test(project, test_name).path) as f:
            assert f.read() == expected

    def test_edit_test_skip(self, project_session, test_utils):
        _, project = project_session.activate()
        test_name = test_utils.create_random_test(project)
        test_module.edit_test(project, test_name, description='', pages=[],
                              steps=EMPTY_STEPS, test_data=[], tags=[], skip=True)
        path = Test(project, test_name).path
        expected = ('\n'
                    'description = \'\'\n\n'
                    'tags = []\n\n'
                    'pages = []\n\n'
                    'skip = True\n\n\n'
                    'def setup(data):\n'
                    '    pass\n\n\n'
                    'def test(data):\n'
                    '    pass\n\n\n'
                    'def teardown(data):\n'
                    '    pass\n')
        with open(path) as f:
            assert f.read() == expected
        # skip is string
        test_module.edit_test(project, test_name, description='', pages=[],
                              steps=EMPTY_STEPS, test_data=[], tags=[],
                              skip='please skip this')
        path = Test(project, test_name).path
        expected = ('\n'
                    'description = \'\'\n\n'
                    'tags = []\n\n'
                    'pages = []\n\n'
                    'skip = \'please skip this\'\n\n\n'
                    'def setup(data):\n'
                    '    pass\n\n\n'
                    'def test(data):\n'
                    '    pass\n\n\n'
                    'def teardown(data):\n'
                    '    pass\n')
        with open(path) as f:
            assert f.read() == expected


class TestEditTestCode:

    def test_edit_test_code_csv_data(self, project_session, test_utils):
        _, project = project_session.activate()
        test_data = [{'key': "'value'"}]
        settings_manager.save_project_settings(project, '{"test_data": "csv"}')
        test_name = test_utils.create_random_test(project)
        test_module.edit_test_code(project, test_name, SAMPLE_TEST_CONTENT, test_data)
        path = test_module.Test(project, test_name).path
        with open(path) as f:
            assert f.read() == SAMPLE_TEST_CONTENT
        path = os.path.join(Project(project).test_directory_path, test_name + '.csv')
        expected = ('key\n' 
                    '\'value\'\n')
        with open(path) as f:
            assert f.read() == expected


class TestDeleteTest:

    def test_delete_test(self, project_session, test_utils):
        _, project = project_session.activate()
        test_one = test_utils.random_string()
        test_two = '{}.{}'.format(test_utils.random_string(), test_utils.random_string())
        test_utils.create_test(project, test_one)
        test_utils.create_test(project, test_two)
        errors_one = test_module.delete_test(project, test_one)
        errors_two = test_module.delete_test(project, test_two)
        assert errors_one == []
        assert errors_two == []
        assert not os.path.isfile(Test(project, test_one).path)
        assert not os.path.isfile(Test(project, test_two).path)

    def test_delete_test_not_exist(self, project_session):
        _, project = project_session.activate()
        errors = test_module.delete_test(project, 'not-exist')
        assert errors == ['Test not-exist does not exist']

    def test_delete_test_with_data(self, project_session, test_utils):
        """"test that when a test is deleted the data files
        are deleted as well
        """
        _, project = project_session.activate()
        test_name = test_utils.create_random_test(project)
        data_path = os.path.splitext(test_module.Test(project, test_name).path)[0] + '.csv'
        open(data_path, 'x').close()
        errors = test_module.delete_test(project, test_name)
        assert errors == []
        assert not os.path.isfile(data_path)


class TestTestExists:

    def test_test_exists(self, project_session, test_utils):
        _, project = project_session.activate()
        test_name = test_utils.create_random_test(project)
        assert Test(project, test_name).exists
        assert not Test(project, 'not_exists_test').exists


class TestTestCode:

    def test_test_code(self, project_session, test_utils):
        _, project = project_session.activate()
        test_name = test_utils.create_random_test(project)
        test = Test(project, test_name)
        with open(test.path, 'w') as f:
            f.write(SAMPLE_TEST_CONTENT)
        assert test.code == SAMPLE_TEST_CONTENT


class TestTestComponents:

    def test_test_components(self, project_session, test_utils):
        _, project = project_session.activate()
        test_name = test_utils.create_random_test(project)
        test = Test(project, test_name)
        with open(test.path, 'w') as f:
            f.write(SAMPLE_TEST_CONTENT)
        components = test.components
        assert components['description'] == 'some description'
        assert components['pages'] == ['page1', 'page2']
        assert components['tags'] == []
        assert components['skip'] is False
        assert components['steps']['setup'] == [{'code': 'page1.func1()',
                                                 'function_name': 'page1.func1',
                                                 'parameters': [],
                                                 'type': 'function-call'}]
        expected_test_steps = [{'code': "page2.func2('a', 'b')",
                                'function_name': 'page2.func2',
                                'parameters': ["'a'", "'b'"],
                                'type': 'function-call'},
                               {'code': 'click(page2.elem1)',
                                'function_name': 'click',
                                'parameters': ['page2.elem1'],
                                'type': 'function-call'}]
        assert components['steps']['test'] == expected_test_steps
        assert components['steps']['teardown'] == []

    def test_test_components_empty_test(self, project_session, test_utils):
        _, project = project_session.activate()
        test_name = test_utils.create_random_test(project)
        test_content = Test(project, test_name).components
        assert test_content['description'] == ''
        assert test_content['pages'] == []
        assert test_content['steps']['setup'] == []
        assert test_content['steps']['test'] == []
        assert test_content['steps']['teardown'] == []

    def test_test_components_pages(self, project_session, test_utils):
        """components['pages'] contains the imported pages and the pages
        defined in the list
        """
        testdir, project = project_session.activate()
        test_name = test_utils.create_random_test(project)
        test_utils.create_page(project, 'page1')
        test_utils.create_page(project, 'page2')
        test_utils.create_page(project, 'module.page3')
        sys.path.append(testdir)
        with open(Test(project, test_name).path, 'w') as f:
            test_content = ('from projects.{}.pages import page1, page2\n'
                            'from projects.{}.pages.module import page3\n'
                            '\n'
                            'pages = ["page4", "module2.page5"]\n'
                            '\n'
                            'def test(data):\n'
                            '    pass\n'.format(project, project))
            f.write(test_content)
        components = Test(project, test_name).components
        expected = ['page1', 'page2', 'module.page3', 'page4', 'module2.page5']
        assert components['pages'].sort() == expected.sort()

    def test_test_components_skip(self, project_session, test_utils):
        _, project = project_session.activate()
        test_name = test_utils.create_random_test(project)
        # default / empty skip is False
        assert Test(project, test_name).components['skip'] is False
        # skip is True
        test_module.edit_test(project, test_name, description='', pages=[],
                              steps=EMPTY_STEPS, test_data=[], tags=[], skip=True)
        assert Test(project, test_name).components['skip'] is True
        # skip is string
        test_module.edit_test(project, test_name, description='', pages=[],
                              steps=EMPTY_STEPS, test_data=[], tags=[], skip='please skip')
        assert Test(project, test_name).components['skip'] == 'please skip'
