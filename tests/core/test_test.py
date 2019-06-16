import os

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


class TestCreateTest:

    def test_create_test(self, project_session, test_utils):
        _, project = project_session.activate()
        test_name = test_utils.random_string()
        errors = test_module.create_test(project, test_name)
        path = Test(project, test_name).path
        assert os.path.isfile(path)
        assert errors == []
        test_code = Test(project, test_name).code
        assert test_code == NEW_TEST_CONTENT

    def test_create_test_name_exists(self, project_session, test_utils):
        _, project = project_session.activate()
        test_name = test_utils.random_string()
        test_module.create_test(project, test_name)
        errors = test_module.create_test(project, test_name)
        assert errors == ['A test with that name already exists']

    def test_create_test_invalid_name(self, project_session):
        _, project = project_session.activate()
        test_name = 'this-is-a-test'
        errors = test_module.create_test(project, test_name)
        assert errors == ['Only letters, numbers and underscores are allowed']

    def test_create_test_with_parents(self, project_session, test_utils):
        _, project = project_session.activate()
        random_dir = test_utils.random_string()
        test_name = '{}.test001'.format(random_dir)
        errors = test_module.create_test(project, test_name)
        assert errors == []
        # verify that each parent dir has __init__.py file
        init_path = os.path.join(Project(project).test_directory_path,
                                 random_dir, '__init__.py')
        assert test_name in Project(project).tests()
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

    def test_rename_test_error(self, project_session, test_utils):
        _, project = project_session.activate()
        test_name = test_utils.create_random_test(project)
        new_test_name = 'new-name'
        errors = test_module.rename_test(project, test_name, new_test_name)
        assert errors == ['Only letters, numbers and underscores are allowed']
        tests = Project(project).tests()
        assert test_name in tests
        assert new_test_name not in tests

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


class TestDuplicateTest:

    def test_duplicate_test(self, project_session, test_utils):
        _, project = project_session.activate()
        test_name = test_utils.create_random_test(project)
        new_test_name = test_utils.random_string()
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

    def test_duplicate_test_name_already_exists(self, project_session, test_utils):
        _, project = project_session.activate()
        test_name = test_utils.create_random_test(project)
        test_name_two = test_utils.create_random_test(project)
        errors = test_module.duplicate_test(project, test_name, test_name_two)
        assert errors == ['A test with that name already exists']

    def test_duplicate_test_error(self, project_session, test_utils):
        _, project = project_session.activate()
        test_name = test_utils.create_random_test(project)
        new_test_name = 'new-name'
        errors = test_module.duplicate_test(project, test_name, new_test_name)
        assert errors == ['Only letters, numbers and underscores are allowed']

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

    def test_edit_test_data_infile(self, project_session, test_utils):
        _, project = project_session.activate()
        test_name = test_utils.create_random_test(project)
        description = 'description'
        pages = ['page1', 'page2']
        test_steps = {
            'setup': [
                {'action': 'click', 'parameters': ['elem1']}
            ],
            'test': [
                {'action': 'send_keys', 'parameters': ['elem2', 'keys']}
            ],
            'teardown': []
        }
        data = [{
            'key': '\'value\''
        }]
        settings_manager.save_project_settings(project, '{"test_data": "infile"}')
        test_module.edit_test(project, test_name, description, pages, test_steps, data, [])
        path = test_module.Test(project, test_name).path
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
            '\n'
            'def setup(data):\n'
            '    click(elem1)\n'
            '\n'
            'def test(data):\n'
            '    send_keys(elem2, keys)\n'
            '\n'
            'def teardown(data):\n'
            '    pass\n')
        with open(path) as f:
            assert f.read() == expected

    def test_edit_test_data_csv(self, project_session, test_utils):
        _, project = project_session.activate()
        test_name = test_utils.create_random_test(project)
        description = 'description'
        pages = []
        test_steps = {
            'setup': [],
            'test': [
                {'action': 'send_keys', 'parameters': ['elem2', 'keys']}
            ],
            'teardown': []
        }
        data = [{
            'key': '\'value\''
        }]
        settings_manager.save_project_settings(project, '{"test_data": "csv"}')
        test_module.edit_test(project, test_name, description, pages, test_steps, data, [])
        path = test_module.Test(project, test_name).path
        expected = (
            '\n'
            'description = \'description\'\n'
            '\n'
            'tags = []\n'
            '\n'
            'pages = []\n'
            '\n'
            'def setup(data):\n'
            '    pass\n'
            '\n'
            'def test(data):\n'
            '    send_keys(elem2, keys)\n'
            '\n'
            'def teardown(data):\n'
            '    pass\n')
        with open(path) as f:
            assert f.read() == expected
        data_path = os.path.join(Project(project).test_directory_path,
                                 '{}.csv'.format(test_name))
        expected = ('key\n'
                    '\'value\'\n')
        with open(data_path) as f:
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


class TestParseSteps:
    
    possible_steps = [
        # action without parameters
        (
            'action()',
            {'method_name': 'action', 'parameters': []}
        ),
        # string parameter
        (
            'action(\'value\')',
            {'method_name': 'action', 'parameters': ["'value'"]}
        ),
        # double string parameter
        (
            'action(\"double_quotes\")',
            {'method_name': 'action', 'parameters': ['"double_quotes"']}
        ),
        # string with spaces
        (
            'action(\'spaces spaces spaces\')',
            {'method_name': 'action', 'parameters': ["'spaces spaces spaces'"]}
        ),
        # double quotes string with single quotes
        (
            'action(\"test \'test2\' test\")',
            {'method_name': 'action', 'parameters': ["\"test \'test2\' test\""]}
        ),
        # single quotes string with double quotes
        (
            'action(\'test \"test2\" test\')',
            {'method_name': 'action', 'parameters': ["\'test \"test2\" test\'"]}
        ),
        # multiple string parameters
        (
            'action(\'one\', \'two\', \'three\')',
            {'method_name': 'action', 'parameters': ["'one'", "'two'", "'three'"]}
        ),
        # tuple parameter
        (
            'action((\'this\', \'is a\', \'tuple\'))',
            {'method_name': 'action', 'parameters': ['(\'this\', \'is a\', \'tuple\')']}
        ),
        # tuple parameter with double quotes string
        (
            'action((\"this\", \"is a\", \"tuple\"))',
            {'method_name': 'action', 'parameters': ['(\"this\", \"is a\", \"tuple\")']}
        ),
        # tuple parameter with ints
        (
            'action((1, 2, 3))',
            {'method_name': 'action', 'parameters': ['(1, 2, 3)']}
        ),
        # tuple and a string parameter
        (
            'action((\'a\', \'b\', \'c\'), \'another\')',
            {'method_name': 'action', 'parameters': ['(\'a\', \'b\', \'c\')', "'another'"]}
        ),
        # two tuple parameters
        (
            'action((\'two\', \'tuples\'), (\'a\', \'b\'))',
            {'method_name': 'action', 'parameters': ['(\'two\', \'tuples\')', '(\'a\', \'b\')']}
        ),
        # dict parameter
        (
            'action({\'test\': \'test\'})',
            {'method_name': 'action', 'parameters': ['{\'test\': \'test\'}']}
        ),
        # dict parameter with double quotes
        (
            'action({\"test\": \"test\"})',
            {'method_name': 'action', 'parameters': ['{\"test\": \"test\"}']}
        ),
        # dict parameter with int values
        (
            'action({\"test\": 2})',
            {'method_name': 'action', 'parameters': ['{\"test\": 2}']}
        ),
        # dict parameter with boolean values
        (
            'action({\"test\": True})',
            {'method_name': 'action', 'parameters': ['{\"test\": True}']}
        ),
        # dict parameter with None values
        (
            'action({\"test\": None})',
            {'method_name': 'action', 'parameters': ['{\"test\": None}']}
        ),
        # dict parameter with multiple keys
        (
            'action({\'test\': \'test\', \'test2\': \'test2\'})',
            {'method_name': 'action', 'parameters': ['{\'test\': \'test\', \'test2\': \'test2\'}']}
        ),
        # dict parameter with multiple double quote keys
        (
            'action({\"test\": \"test\", \"test2\": \"test2\"})',
            {'method_name': 'action', 'parameters': ['{\"test\": \"test\", \"test2\": \"test2\"}']}
        ),
        # list parameter
        (
            'action([\'a\', \'b\'])',
            {'method_name': 'action', 'parameters': ['[\'a\', \'b\']']}
        ),
        # list parameter with double quote strings
        (
            'action([\"a\", \"b\"])',
            {'method_name': 'action', 'parameters': ['[\"a\", \"b\"]']}
        ),
        # list parameter with ints
        (
            'action([1, 2])',
            {'method_name': 'action', 'parameters': ['[1, 2]']}
        ),
        # int parameter
        (
            'action(123)',
            {'method_name': 'action', 'parameters': ['123']}
        ),
        # float parameter
        (
            'action(123.4)',
            {'method_name': 'action', 'parameters': ['123.4']}
        ),
        # boolean parameter
        (
            'action(True)',
            {'method_name': 'action', 'parameters': ['True']}
        ),
        # None parameter
        (
            'action(None)',
            {'method_name': 'action', 'parameters': ['None']}
        ),
        # object attribute
        (
            'action(page.element)',
            {'method_name': 'action', 'parameters': ['page.element']}
        ),
        # object attribute and a string
        (
            'action(page.element, \'test\')',
            {'method_name': 'action', 'parameters': ['page.element', '\'test\'']}
        ),
        # string with commas
        (
            'action(\'string, with, commas\')',
            {'method_name': 'action', 'parameters': ["'string, with, commas'"]}
        ),
        # page object method without parameters
        (
            'some_page.some_action()',
            {'method_name': 'some_page.some_action', 'parameters': []}
        )
    ]

    @pytest.mark.parametrize('step, expected', possible_steps)
    def test_parse_step(self, step, expected):
        parsed = test_module._parse_step(step)
        assert parsed == expected


class TestGetParsedSteps:

    def test__get_parsed_steps(self):
        def func1():
            min(2, 3)
            max(2, 3)
        result = test_module._get_parsed_steps(func1)
        expected = [
            {'method_name': 'min', 'parameters': ['2', '3']},
            {'method_name': 'max', 'parameters': ['2', '3']}
        ]
        assert result == expected

    def test__get_parsed_steps_empty_lines(self):
        def func1():
            min(2, 3)
            max(2, 3)
        result = test_module._get_parsed_steps(func1)
        expected = [
            {'method_name': 'min', 'parameters': ['2', '3']},
            {'method_name': 'max', 'parameters': ['2', '3']}
        ]
        assert result == expected

    def test__get_parsed_steps_pass(self):
        def func1():
            pass
        result = test_module._get_parsed_steps(func1)
        assert result == []


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
        test_content = test.components
        assert test_content['description'] == 'some description'
        assert test_content['pages'] == ['page1', 'page2']
        assert test_content['steps']['setup'] == [{'method_name': 'page1.func1', 'parameters': []}]
        expected_test_steps = [{'method_name': 'page2.func2', 'parameters': ["'a'", "'b'"]},
                               {'method_name': 'click', 'parameters': ['page2.elem1']}]
        assert test_content['steps']['test'] == expected_test_steps
        assert test_content['steps']['teardown'] == []

    def test_test_components_empty_test(self, project_session, test_utils):
        _, project = project_session.activate()
        test_name = test_utils.create_random_test(project)
        test_content = Test(project, test_name).components
        assert test_content['description'] == ''
        assert test_content['pages'] == []
        assert test_content['steps']['setup'] == []
        assert test_content['steps']['test'] == []
        assert test_content['steps']['teardown'] == []
