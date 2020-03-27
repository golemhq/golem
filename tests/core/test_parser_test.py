import re

import pytest

from golem.core import test_parser


class TestFunctionBodyCode:

    def test_function_body_code(self):
        def function1():
            pass
        code = test_parser.function_body_code(function1)
        assert code == '            pass\n'

        def function2(param1,
                      param2):
            while param2:
                print('test')

        code = test_parser.function_body_code(function2)
        expected = "            while param2:\n                print('test')\n"
        assert code == expected

        def function3():
            # comment
            pass
        code = test_parser.function_body_code(function3)
        assert code == '            # comment\n            pass\n'


class TestReplaceSubstrings:

    def test_replace_substrings(self):
        # no parentheses
        code, replacements = test_parser._replace_substrings('no parentheses',
                                                             '(', ')')
        assert code == 'no parentheses'
        assert replacements == []
        # one parenthesis
        code, replacements = test_parser._replace_substrings('this is a (test) string',
                                                             '(', ')')
        assert len(replacements) == 1
        assert replacements[0][1] == '(test)'
        assert code == 'this is a {} string'.format(replacements[0][0])
        # two parentheses
        code, replacements = test_parser._replace_substrings('this is (a) (test) string',
                                                             '(', ')')
        assert len(replacements) == 2
        assert code == 'this is {} {} string'.format(replacements[0][0], replacements[1][0])
        # nested parentheses
        code, replacements = test_parser._replace_substrings('this is (a (nested) ) test',
                                                             '(', ')')
        assert len(replacements) == 1
        assert code == 'this is {} test'.format(replacements[0][0])
        # new lines inside parentheses
        code, replacements = test_parser._replace_substrings('this is (a \ntest) string',
                                                             '(', ')')
        assert len(replacements) == 1
        assert code == 'this is {} string'.format(replacements[0][0])
        code, replacements = test_parser._replace_substrings('this is (\na test\n) string',
                                                             '(', ')')
        assert len(replacements) == 1
        assert code == 'this is {} string'.format(replacements[0][0])


class TestReplaceRePattern:

    def test_replace_re_pattern(self):
        pattern = re.compile(r'(\"\"\".+?\"\"\")', re.S)
        original_code = 'this is a """test""" string'
        code, replacements = test_parser._replace_re_pattern(original_code, pattern)
        assert replacements[0][1] == '"""test"""'
        assert code.replace(replacements[0][0], replacements[0][1]) == original_code

        original_code = 'this is """a""" """test""" string'
        code, replacements = test_parser._replace_re_pattern(original_code, pattern)
        assert replacements[0][1] == '"""a"""'
        assert replacements[1][1] == '"""test"""'


class TestSplitCodeIntoBlocks:

    def test_split_code_into_blocks(self):
        code = ('block_one()\n'
                '# comment\n'
                'if foo:\n'
                '    print("bar")\n')
        blocks = test_parser._split_code_into_blocks(code)
        assert len(blocks) == 3
        assert blocks[0] == 'block_one()'
        assert blocks[1] == '# comment'
        assert blocks[2] == 'if foo:\n    print("bar")'
        # empty lines
        code = ("print('foo')\n"
                "\n"
                "\n"
                "bar = 1 + 1\n")
        blocks = test_parser._split_code_into_blocks(code)
        assert len(blocks) == 2
        assert blocks[0] == "print('foo')"
        assert blocks[1] == "bar = 1 + 1"
        # empty lines
        code = ("\n"
                "\n"
                "bar = 1 + 1\n")
        blocks = test_parser._split_code_into_blocks(code)
        assert len(blocks) == 1
        assert blocks[0] == "bar = 1 + 1"
        # if-else
        code = ('if foo:\n'
                '    print("bar")\n'
                'else:'
                '    pass')
        blocks = test_parser._split_code_into_blocks(code)
        assert len(blocks) == 1
        # nested if
        code = ('if foo:\n'
                '    if 2 = 2:\n'
                '        print("hello")\n'
                '    else:\n'
                '        print("bye")\n'
                'else:\n'
                '    pass')
        blocks = test_parser._split_code_into_blocks(code)
        assert len(blocks) == 1
        # if-elif-else
        code = ('if foo:\n'
                '    print("bar")\n'
                'elif bar:\n'
                '    pass\n'
                'else:\n'
                '    pass')
        blocks = test_parser._split_code_into_blocks(code)
        assert len(blocks) == 1
        # for-in loop
        code = ('for x in y:\n'
                '    print("bar")\n'
                '    if x == "test":\n'
                '        print("test")\n'
                '    else:\n'
                '        print("else")\n')
        blocks = test_parser._split_code_into_blocks(code)
        assert len(blocks) == 1
        # try-except-else-finally block
        code = ('try:\n'
                '    int("bar")\n'
                'except ValueError:\n'
                '    pass\n'
                'except Exception as e:\n'
                '    pass\n'
                'else:\n'
                '    pass\n'
                'finally:\n'
                '    pass')
        blocks = test_parser._split_code_into_blocks(code)
        assert len(blocks) == 1


class TestCodeBlockIsFunctionCall:

    function_calls = [
        'function()',
        'function(1)',
        'function(1, 2)',
        'function("foo")',
        'function("foo", "bar")',
        'function((1, 2), ("foo", "bar"))',
        'function({"foo": "bar"})',
        'function(\n    "foo",\n    "bar"\n)',
        'function(keyword="foo")',
        'module.function()',
        'module.function("foo")'
    ]

    @pytest.mark.parametrize('test_string', function_calls)
    def test_code_block_is_function_call(self, test_string):
        assert test_parser._code_block_is_function_call(test_string)

    not_function_calls = [
        'foo().bar()',
        'test = 1',
        '# foo()',
        'with open(path) as f:\n    print(f)\n',
        'if foo:\n    print(bar)',
        'if(foo):\n    print(bar)',
        'while foo:\n    print(bar)',
        'foo = print("bar")'
    ]

    @pytest.mark.parametrize('test_string', not_function_calls)
    def test_code_block_is_function_call_false(self, test_string):
        assert not test_parser._code_block_is_function_call(test_string)


class TestParseFunctionCall:

    function_calls = [
        # action without parameters
        (
            'action()',
            ('action', [])
        ),
        # empty spaces
        (
            'action(  )',
            ('action', [])
        ),
        # string parameter
        (
            'action(\'value\')',
            ('action', ["'value'"])
        ),
        # double string parameter
        (
            'action(\"double_quotes\")',
            ('action', ['"double_quotes"'])
        ),
        # string with spaces
        (
            'action(\'spaces spaces spaces\')',
            ('action', ["'spaces spaces spaces'"])
        ),
        # double quotes string with single quotes
        (
            'action(\"test \'test2\' test\")',
            ('action', ["\"test \'test2\' test\""])
        ),
        # single quotes string with double quotes
        (
            'action(\'test \"test2\" test\')',
            ('action', ["\'test \"test2\" test\'"])
        ),
        # multiple string parameters
        (
            'action(\'one\', \'two\', \'three\')',
            ('action', ["'one'", "'two'", "'three'"])
        ),
        # tuple parameter
        (
            'action((\'this\', \'is a\', \'tuple\'))',
            ('action', ['(\'this\', \'is a\', \'tuple\')'])
        ),
        # tuple parameter with double quotes string
        (
            'action((\"this\", \"is a\", \"tuple\"))',
            ('action', ['(\"this\", \"is a\", \"tuple\")'])
        ),
        # tuple parameter with ints
        (
            'action((1, 2, 3))',
            ('action', ['(1, 2, 3)'])
        ),
        # tuple and a string parameter
        (
            'action((\'a\', \'b\', \'c\'), \'another\')',
            ('action', ['(\'a\', \'b\', \'c\')', "'another'"])
        ),
        # two tuple parameters
        (
            'action((\'two\', \'tuples\'), (\'a\', \'b\'))',
            ('action', ['(\'two\', \'tuples\')', '(\'a\', \'b\')'])
        ),
        # dict parameter
        (
            'action({\'test\': \'test\'})',
            ('action', ['{\'test\': \'test\'}'])
        ),
        # dict parameter with double quotes
        (
            'action({\"test\": \"test\"})',
            ('action', ['{\"test\": \"test\"}'])
        ),
        # dict parameter with int values
        (
            'action({\"test\": 2})',
            ('action', ['{\"test\": 2}'])
        ),
        # dict parameter with boolean values
        (
            'action({\"test\": True})',
            ('action', ['{\"test\": True}'])
        ),
        # dict parameter with None values
        (
            'action({\"test\": None})',
            ('action', ['{\"test\": None}'])
        ),
        # dict parameter with multiple keys
        (
            'action({\'test\': \'test\', \'test2\': \'test2\'})',
            ('action', ['{\'test\': \'test\', \'test2\': \'test2\'}'])
        ),
        # dict parameter with multiple double quote keys
        (
            'action({\"test\": \"test\", \"test2\": \"test2\"})',
            ('action', ['{\"test\": \"test\", \"test2\": \"test2\"}'])
        ),
        # list parameter
        (
            'action([\'a\', \'b\'])',
            ('action', ['[\'a\', \'b\']'])
        ),
        # list parameter with double quote strings
        (
            'action([\"a\", \"b\"])',
            ('action', ['[\"a\", \"b\"]'])
        ),
        # list parameter with ints
        (
            'action([1, 2])',
            ('action', ['[1, 2]'])
        ),
        # int parameter
        (
            'action(123)',
            ('action', ['123'])
        ),
        # float parameter
        (
            'action(123.4)',
            ('action', ['123.4'])
        ),
        # boolean parameter
        (
            'action(True)',
            ('action', ['True'])
        ),
        # None parameter
        (
            'action(None)',
            ('action', ['None'])
        ),
        # object attribute
        (
            'action(page.element)',
            ('action', ['page.element'])
        ),
        # object attribute and a string
        (
            'action(page.element, \'test\')',
            ('action', ['page.element', '\'test\''])
        ),
        # string with commas
        (
            'action(\'string, with, commas\')',
            ('action', ["'string, with, commas'"])
        ),
        # page object method without parameters
        (
            'some_page.some_action()',
            ('some_page.some_action', [])
        ),
        # page object method with parameters
        (
            'some_page.some_action(1, "test")',
            ('some_page.some_action', ['1', '"test"'])
        ),
        # nested tuples
        (
            'action(((1,2), "1"), (3,4))',
            ('action', ['((1,2), "1")', '(3,4)'])
        ),
        # new line inside string
        (
            'step.action(\'if(True):\n    print("True")\')',
            ('step.action', ['\'if(True):\n    print("True")\''])
        )
    ]

    @pytest.mark.parametrize('call, expected', function_calls)
    def test_parse_function_call(self, call, expected):
        parsed = test_parser._parse_function_call(call)
        assert parsed == expected


class TestParseFunctionSteps:

    def test_parse_function_steps(self):
        def function():
            print('foo')
            bar = False
            if bar:
                print('baz')
            # comment
            str('test').replace('s', 'x')

        steps = test_parser.parse_function_steps(function)
        expected_steps = [
            {'type': 'function-call', 'code': "print('foo')", 'function_name': 'print', 'parameters': ["'foo'"]},
            {'type': 'code-block', 'code': 'bar = False'},
            {'type': 'code-block', 'code': "if bar:\n    print('baz')"},
            {'type': 'code-block', 'code': '# comment'},
            {'type': 'code-block', 'code': "str('test').replace('s', 'x')"}
        ]
        assert steps == expected_steps

    def test_parse_function_pass(self):
        """Functions with only `pass` in the body return no steps"""
        def function1():
            pass
        steps = test_parser.parse_function_steps(function1)
        assert steps == []

        def function2():

            pass
        steps = test_parser.parse_function_steps(function2)
        assert steps == []

        def function3():
            print('foo')
            pass
        steps = test_parser.parse_function_steps(function3)
        assert len(steps) == 2
        assert steps[0]['function_name'] == 'print'
        assert steps[1]['code'] == 'pass'

    def test_parse_function_nested(self):
        def function1():
            print([
                'foo',
                'bar'
            ])
            bar = (
                [False, True],
                0)

        steps = test_parser.parse_function_steps(function1)
        expected_steps = [
            {
                'type': 'function-call',
                'code': "print([\n    'foo',\n    'bar'\n])",
                'function_name': 'print',
                'parameters': ["[    'foo',    'bar']"]
            },
            {
                'type': 'code-block',
                'code': 'bar = (\n    [False, True],\n    0)'
            }
        ]
        assert steps == expected_steps


class TestParseImportedPages:

    def test_parse_imported_pages(self):
        code = ('from projects.project_name.pages import page1\n'
                'from projects.project_name.pages import page2, page3\n'
                'from projects.project_name.pages.module import page4\n'
                'from projects.project_name.pages.module import page5, page6\n'
                'from projects.project_name.pages.module.sub_module import page7\n'
                '\n'
                'def test(data):\n'
                '    pass')
        pages = test_parser.parse_imported_pages(code)
        assert pages == ['page1', 'page2', 'page3', 'module.page4', 'module.page5',
                         'module.page6', 'module.sub_module.page7']
        # new line between imports
        code = ('from projects.project_name.pages import page1\n'
                '\n'
                'from projects.project_name.pages import page2\n'
                '\n'
                'def test(data):\n'
                '    pass')
        pages = test_parser.parse_imported_pages(code)
        assert pages == ['page1', 'page2']
        # invalid import format
        code = ('from project_name.pages import page1\n'
                'from projects.project_name import page2\n'
                'from project_name.pages import *\n'
                'from project_name.pages.page1 import *\n'
                '\n'
                'def test(data):\n'
                '    pass')
        pages = test_parser.parse_imported_pages(code)
        assert pages == []
