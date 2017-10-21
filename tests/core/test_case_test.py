import os
from collections import OrderedDict

from golem.core import test_case


class Test__parse_step:

    possible_steps = [
        {
            'src': 'action()',
            'expected': {'method_name': 'action', 'parameters': []}
        },
        {
            'src': 'action(\'value\')',
            'expected': {'method_name': 'action', 'parameters': ['value']}
        },
        {
            'src': 'action(\"double_quotes\")',
            'expected': {'method_name': 'action', 'parameters': ['double_quotes']}
        },
        {
            'src': 'action(\'spaces spaces spaces\')',
            'expected': {'method_name': 'action', 'parameters': ['spaces spaces spaces']}
        },
        {
            'src': 'action(\'one\', \'two\', \'three\')',
            'expected': {'method_name': 'action', 'parameters': ['one', 'two', 'three']}
        },
        {
            'src': 'action((\'this\', \'is a\', \'tuple\'))',
            'expected': {'method_name': 'action', 'parameters': ['(\'this\', \'is a\', \'tuple\')']}
        },
        {
            'src': 'action((\'a\', \'b\', \'c\'), \'another\')',
            'expected': {'method_name': 'action', 'parameters': ['(\'a\', \'b\', \'c\')', 'another']}
        },
        {
            'src': 'action((\'two\', \'tuples\'), (\'a\', \'b\'))',
            'expected': {'method_name': 'action', 'parameters': ['(\'two\', \'tuples\')', '(\'a\', \'b\')']}
        },
        {
            'src': 'action(page.element)',
            'expected': {'method_name': 'action', 'parameters': ['page.element']}
        },
        {
            'src': 'action(\'string, with, commas\')',
            'expected': {'method_name': 'action', 'parameters': ['string, with, commas']}
        },
        {
            'src': 'some_page.some_action()',
            'expected': {'method_name': 'some_page.some_action', 'parameters': []}
        }
    ]

    def test_parse_step(self):
        for step in self.possible_steps:
            parsed = test_case._parse_step(step['src'])
            assert step['expected'] == parsed


class Test_format_parameter:
    possible_inputs = [
        {
            'param': 'test',
            'action': 'click',
            'expected': 'test'
        },
        {
            'param': '123',
            'action': 'click',
            'expected': 123
        },
        {
            'param': 'test test',
            'action': 'click',
            'expected': 'test test'
        },
        # {
        #     'input': {'action': 'click', 'parameters': ["('id', 'searchInput')"]},
        #     'expected': '(\'id\', \'searchInput\')'
        # },
        # {
        #     'input': {'action': 'click', 'parameters': ["('id', 'searchInput', 'some name')"]},
        #     'expected': '(\'id\', \'searchInput\', \'some name\')'
        # },
        # {
        #     'input': {'action': 'click', 'parameters': ['some string']},
        #     'expected': 'some string'
        # },
        # {
        #     'input': {'action': 'click', 'parameters': ["some string"]},
        #     'expected': 'some string'
        # },
        # {
        #     'input': {'action': 'click', 'parameters': ['string one', 'string two']},
        #     'expected': 'string one, string two'
        # },
        # {
        #     'input': {'action': 'click', 'parameters': ["string 'inside' string"]},
        #     'expected': 'string \'inside\' string'
        # },
        # {
        #     'input': {'action': 'click', 'parameters': ['123']},
        #     'expected': 123
        # },
        # {
        #     'input': {'action': 'send keys', 'parameters': ["('id', 'searchInput')", 'automation']},
        #     'expected': '(\'id\', \'searchInput\'), \'automation\''
        # },
        # {
        #     'input': {'action': 'send keys', 'parameters': ["(\'id\', \"searchInput[attr=\'value\']\")"]},
        #     'expected': '(\'id\', \"searchInput[attr=\'value\']\")'
        # },
        # {
        #     'input': {'action': 'send keys', 'parameters': ['\{\'a\': \'b\', \'c\': \'d\'\}']},
        #     'expected': '\{\'a\': \'b\', \'c\': \'d\'\}'
        # }
    ]

    def test_format_parameters(self):
        param_formatter = test_case.Param_formatter('', '', '')
        for step in self.possible_inputs:
            parsed = param_formatter.format_param(step['param'], step['action'])
            print(parsed)
            assert step['expected'] == parsed


