import os
import json

import pytest

from golem.core import test_case, test_execution, settings_manager


SAMPLE_TEST_CONTENT = """
description = 'some description'

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

pages = []

def setup(data):
    pass

def test(data):
    pass

def teardown(data):
    pass

"""


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
        parsed = test_case._parse_step(step)
        assert parsed == expected


class TestGetParsedSteps:

    def test__get_parsed_steps(self):
        def func1():
            min(2, 3)
            max(2, 3)
        result = test_case._get_parsed_steps(func1)
        expected = [
            {'method_name': 'min', 'parameters': ['2', '3']},
            {'method_name': 'max', 'parameters': ['2', '3']}
        ]
        assert result == expected

    def test__get_parsed_steps_empty_lines(self):
        def func1():
            min(2, 3)
            max(2, 3)
        result = test_case._get_parsed_steps(func1)
        expected = [
            {'method_name': 'min', 'parameters': ['2', '3']},
            {'method_name': 'max', 'parameters': ['2', '3']}
        ]
        assert result == expected

    def test__get_parsed_steps_pass(self):
        def func1():
            pass
        result = test_case._get_parsed_steps(func1)
        assert result == []


class TestGetTestCaseContent:

    def test_get_test_case_content(self, project_class):
        test_name = 'some_test_case'
        path = os.path.join(project_class.path, 'tests', test_name + '.py')
        with open(path, 'w') as ff:
            ff.write(SAMPLE_TEST_CONTENT)
        test_content = test_case.get_test_case_content(project_class.testdir, project_class.name, test_name)
        assert test_content['description'] == 'some description'
        assert test_content['pages'] == ['page1', 'page2']
        assert test_content['steps']['setup'] == [{'method_name': 'page1.func1', 'parameters': []}]
        expected_test_steps = [{'method_name': 'page2.func2', 'parameters': ["'a'", "'b'"]},
                               {'method_name': 'click', 'parameters': ['page2.elem1']}]
        assert test_content['steps']['test'] == expected_test_steps
        assert test_content['steps']['teardown'] == []

    def test_get_test_case_content_empty_test(self, project_function):
        testdir = project_function.testdir
        project = project_function.name
        test_name = 'some_test_case'
        test_case.new_test_case(testdir, project, [], test_name)
        test_content = test_case.get_test_case_content(testdir, project, test_name)
        assert test_content['description'] == ''
        assert test_content['pages'] == []
        assert test_content['steps']['setup'] == []
        assert test_content['steps']['test'] == []
        assert test_content['steps']['teardown'] == []


class TestGetTestCaseCode:

    def test_get_test_case_code(self, project_class):
        test_name = 'some_test_case2'
        path = os.path.join(project_class.path, 'tests', test_name + '.py')
        with open(path, 'w') as f:
            f.write(SAMPLE_TEST_CONTENT)
        test_code = test_case.get_test_case_code(path)
        assert test_code == SAMPLE_TEST_CONTENT


class TestNewTestCase:

    def test_new_test_case(self, project_class):
        testdir = project_class.testdir
        project = project_class.name
        test_name = 'new_test_case_001'
        parents = ['aaaa', 'bbbb']
        errors = test_case.new_test_case(testdir, project, parents, test_name)
        path = os.path.join(project_class.path, 'tests', os.sep.join(parents), test_name+'.py')
        assert os.path.isfile(path)
        assert errors == []
        test_code = test_case.get_test_case_code(path)
        assert test_code == NEW_TEST_CONTENT

    def test_new_test_case_file_exists(self, project_class):
        testdir = project_class.testdir
        project = project_class.name
        test_name = 'new_test_case_002'
        parents = ['aaaa', 'bbbb']
        test_case.new_test_case(testdir, project, parents, test_name)
        errors = test_case.new_test_case(testdir, project, parents, test_name)
        assert errors == ['a test with that name already exists']

    def test_new_test_case_with_parents(self, project_session):            
        testdir = project_session.testdir
        project = project_session.name
        test_name = 'test_new_test_0001'
        parents = ['asd01', 'asd02']
        errors = test_case.new_test_case(testdir, project, parents, test_name)
        path = os.path.join(project_session.path, 'tests', os.sep.join(parents), test_name + '.py')
        assert errors == []
        assert os.path.isfile(path)
        # verify that each parent dir has __init__.py file
        init_path = os.path.join(project_session.path, 'tests', 'asd01', '__init__.py')
        assert os.path.isfile(init_path)
        init_path = os.path.join(project_session.path, 'tests', 'asd01', 'asd02', '__init__.py')
        assert os.path.isfile(init_path)

    def test_new_test_case_with_parents_already_exist(self, project_session):
        testdir = project_session.testdir
        project = project_session.name
        test_name1 = 'test_new_0004'
        test_name2 = 'test_new_0005'
        parents = ['asf01']
        test_case.new_test_case(testdir, project, parents, test_name1)
        errors = test_case.new_test_case(testdir, project, parents, test_name2)
        path = os.path.join(project_session.path, 'tests', os.sep.join(parents), test_name2 + '.py')
        assert errors == []
        assert os.path.isfile(path)


class TestSaveTestCase:

    def test_save_test_case_data_infile(self, project_function):
        testdir = project_function.testdir
        project = project_function.name
        test_case.new_test_case(testdir, project, ['a', 'b'], 'test_one')
        description = 'description'
        page_objects = ['page1', 'page2']
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
        settings_manager.save_global_settings(testdir, json.dumps({'test_data': 'infile'}))
        test_case.save_test_case(testdir, project, 'a.b.test_one', description,
                                 page_objects, test_steps, data)
        path = os.path.join(project_function.path, 'tests', 'a', 'b', 'test_one.py')
        expected = (
            '\n'
            'description = \'description\'\n'
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

    def test_save_test_case_data_csv(self, project_function):
        testdir = project_function.testdir
        project = project_function.name
        test_case.new_test_case(testdir, project, ['a', 'b'], 'test_one')
        description = 'description'
        page_objects = []
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
        settings_manager.save_global_settings(testdir, json.dumps({'test_data': 'csv'}))
        test_case.save_test_case(testdir, project, 'a.b.test_one', description,
                                 page_objects, test_steps, data)
        path = os.path.join(project_function.path, 'tests', 'a', 'b', 'test_one.py')
        expected = (
            '\n'
            'description = \'description\'\n'
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
        data_path = os.path.join(project_function.path, 'tests', 'a', 'b', 'test_one.csv')
        expected = ('key\n'
                    '\'value\'\n')
        with open(data_path) as f:
            assert f.read() == expected


class TestSaveTestCaseCode:

    def test_save_test_case_code_csv_data(self, project_function):
        testdir = project_function.testdir
        project = project_function.name
        test_name = 'test_one'
        test_data = [{'key': "'value'"}]
        test_execution.settings['test_data'] = 'csv'
        test_case.new_test_case(testdir, project, [], test_name)
        test_case.save_test_case_code(testdir, project, test_name,
                                      SAMPLE_TEST_CONTENT, test_data)
        path = os.path.join(project_function.path, 'tests', test_name + '.py')
        with open(path) as f:
            assert f.read() == SAMPLE_TEST_CONTENT
        path = os.path.join(project_function.path, 'tests', test_name + '.csv')
        expected = ('key\n' 
                    '\'value\'\n')
        with open(path) as f:
            assert f.read() == expected
