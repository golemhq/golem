import os
from collections import OrderedDict

from golem.core import test_case


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


# class Test_format_parameter:
#     possible_inputs = [
#         {
#             'param': 'test',
#             'expected': 'test'
#         },
#         {
#             'param': '123',
#             'action': 'click',
#             'expected': 123
#         },
#         {
#             'param': 'test test',
#             'action': 'click',
#             'expected': 'test test'
#         }
#     ]

#     def test_format_parameters(self):
#         param_formatter = test_case.Param_formatter('', '', '')
#         for step in self.possible_inputs:
#             parsed = param_formatter.format_param(step['param'], step['action'])
#             print(parsed)
#             assert step['expected'] == parsed


