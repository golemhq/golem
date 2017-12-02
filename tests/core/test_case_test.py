import os
from collections import OrderedDict

from tests.fixtures import testdir_fixture, random_project_fixture, project_fixture

from golem.core import test_case


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


class Test__parse_step:

    possible_steps = [
        # action without parameters
        {
            'src': 'action()',
            'expected': {'method_name': 'action', 'parameters': []}
        },
        # string parameter
        {
            'src': 'action(\'value\')',
            'expected': {'method_name': 'action', 'parameters': ["'value'"]}
        },
        # double string parameter
        {
            'src': 'action(\"double_quotes\")',
            'expected': {'method_name': 'action', 'parameters': ['"double_quotes"']}
        },
        # string with spaces
        {
            'src': 'action(\'spaces spaces spaces\')',
            'expected': {'method_name': 'action', 'parameters': ["'spaces spaces spaces'"]}
        },
        # double quotes string with single quotes
        {
            'src': 'action(\"test \'test2\' test\")',
            'expected': {'method_name': 'action', 'parameters': ["\"test \'test2\' test\""]}
        },
        # single quotes string with double quotes
        {
            'src': 'action(\'test \"test2\" test\')',
            'expected': {'method_name': 'action', 'parameters': ["\'test \"test2\" test\'"]}
        },
        # multiple string parameters
        {
        'src': 'action(\'one\', \'two\', \'three\')',
            'expected': {'method_name': 'action', 'parameters': ["'one'", "'two'", "'three'"]}
        },
        # tuple parameter
        {
            'src': 'action((\'this\', \'is a\', \'tuple\'))',
            'expected': {'method_name': 'action', 'parameters': ['(\'this\', \'is a\', \'tuple\')']}
        },
        # tuple parameter with double quotes string
        {
            'src': 'action((\"this\", \"is a\", \"tuple\"))',
            'expected': {'method_name': 'action', 'parameters': ['(\"this\", \"is a\", \"tuple\")']}
        },
        # tuple parameter with ints
        {
            'src': 'action((1, 2, 3))',
            'expected': {'method_name': 'action', 'parameters': ['(1, 2, 3)']}
        },
        # tuple and a string parameter
        {
            'src': 'action((\'a\', \'b\', \'c\'), \'another\')',
            'expected': {'method_name': 'action', 'parameters': ['(\'a\', \'b\', \'c\')', "'another'"]}
        },
        # two tuple parameters
        {
            'src': 'action((\'two\', \'tuples\'), (\'a\', \'b\'))',
            'expected': {'method_name': 'action', 'parameters': ['(\'two\', \'tuples\')', '(\'a\', \'b\')']}
        },
        # dict parameter
        {
            'src': 'action({\'test\': \'test\'})',
            'expected': {'method_name': 'action', 'parameters': ['{\'test\': \'test\'}']}
        },
        # dict parameter with double quotes
        {
            'src': 'action({\"test\": \"test\"})',
            'expected': {'method_name': 'action', 'parameters': ['{\"test\": \"test\"}']}
        },
        # dict parameter with int values
        {
            'src': 'action({\"test\": 2})',
            'expected': {'method_name': 'action', 'parameters': ['{\"test\": 2}']}
        },
        # dict parameter with boolean values
        {
            'src': 'action({\"test\": True})',
            'expected': {'method_name': 'action', 'parameters': ['{\"test\": True}']}
        },
        # dict parameter with None values
        {
            'src': 'action({\"test\": None})',
            'expected': {'method_name': 'action', 'parameters': ['{\"test\": None}']}
        },
        # dict parameter with multiple keys
        {
            'src': 'action({\'test\': \'test\', \'test2\': \'test2\'})',
            'expected': {'method_name': 'action', 'parameters': ['{\'test\': \'test\', \'test2\': \'test2\'}']}
        },
        # dict parameter with multiple double quote keys
        {
            'src': 'action({\"test\": \"test\", \"test2\": \"test2\"})',
            'expected': {'method_name': 'action', 'parameters': ['{\"test\": \"test\", \"test2\": \"test2\"}']}
        },
        # list parameter
        {
            'src': 'action([\'a\', \'b\'])',
            'expected': {'method_name': 'action', 'parameters': ['[\'a\', \'b\']']}
        },
        # list parameter with double quote strings
        {
            'src': 'action([\"a\", \"b\"])',
            'expected': {'method_name': 'action', 'parameters': ['[\"a\", \"b\"]']}
        },
        # list parameter with ints
        {
            'src': 'action([1, 2])',
            'expected': {'method_name': 'action', 'parameters': ['[1, 2]']}
        },
        # int parameter
        {
            'src': 'action(123)',
            'expected': {'method_name': 'action', 'parameters': ['123']}
        },
        # float parameter
        {
            'src': 'action(123.4)',
            'expected': {'method_name': 'action', 'parameters': ['123.4']}
        },
        # boolean parameter
        {
            'src': 'action(True)',
            'expected': {'method_name': 'action', 'parameters': ['True']}
        },
        # None parameter
        {
            'src': 'action(None)',
            'expected': {'method_name': 'action', 'parameters': ['None']}
        },
        # object attribute
        {
            'src': 'action(page.element)',
            'expected': {'method_name': 'action', 'parameters': ['page.element']}
        },
        # object attribute and a string
        {
            'src': 'action(page.element, \'test\')',
            'expected': {'method_name': 'action', 'parameters': ['page.element', '\'test\'']}
        },
        # string with commas
        {
            'src': 'action(\'string, with, commas\')',
            'expected': {'method_name': 'action', 'parameters': ["'string, with, commas'"]}
        },
        # page object method without parameters
        {
            'src': 'some_page.some_action()',
            'expected': {'method_name': 'some_page.some_action', 'parameters': []}
        }
    ]

    def test_parse_step(self):
        for step in self.possible_steps:
            parsed = test_case._parse_step(step['src'])
            assert step['expected'] == parsed


class Test_get_test_case_content:

    def test_get_test_case_content(self, testdir_fixture, random_project_fixture):

        test_name = 'some_test_case'
        root_path = random_project_fixture['testdir_fixture']['path']
        project = random_project_fixture['name']
        path = os.path.join(root_path, 'projects', project,
                            'tests', test_name + '.py')
        with open(path, 'w') as ff:
            ff.write(SAMPLE_TEST_CONTENT)
        test_content = test_case.get_test_case_content(root_path, project, test_name)
        assert test_content['description'] == 'some description'
        assert test_content['pages'] == ['page1', 'page2']
        assert test_content['steps']['setup'] == [{'method_name': 'page1.func1', 'parameters': []}]
        assert test_content['steps']['test'] == [{'method_name': 'page2.func2', 'parameters': ["'a'", "'b'"]}, {'method_name': 'click', 'parameters': ['page2.elem1']}]
        assert test_content['steps']['teardown'] == []


class Test_get_test_case_code:

    def test_get_test_case_code(self, testdir_fixture, random_project_fixture):
        test_name = 'some_test_case2'
        root_path = random_project_fixture['testdir_fixture']['path']
        project = random_project_fixture['name']
        path = os.path.join(root_path, 'projects', project, 'tests', test_name + '.py')
        with open(path, 'w') as ff:
            ff.write(SAMPLE_TEST_CONTENT)
        test_code = test_case.get_test_case_code(path)
        assert test_code == SAMPLE_TEST_CONTENT


class Test_new_test_case:

    def test_new_test_case(self, testdir_fixture, project_fixture):

        root_path = testdir_fixture['path']
        project = project_fixture['name']
        test_name = 'new_test_case_001'
        parents = ['aaaa', 'bbbb']
        errors = test_case.new_test_case(root_path, project, parents, test_name)

        path = os.path.join(root_path, 'projects', project, 'tests',
                            os.sep.join(parents), test_name + '.py')
        assert os.path.isfile(path)
        assert errors == []
        test_code = test_case.get_test_case_code(path)
        assert test_code == NEW_TEST_CONTENT


    def test_new_test_case_file_exists(self, testdir_fixture, project_fixture):

        root_path = testdir_fixture['path']
        project = project_fixture['name']
        test_name = 'new_test_case_002'
        parents = ['aaaa', 'bbbb']
        test_case.new_test_case(root_path, project, parents, test_name)

        errors = test_case.new_test_case(root_path, project, parents, test_name)

        assert errors == ['A test with that name already exists']


