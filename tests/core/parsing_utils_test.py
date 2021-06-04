import ast

from golem.core import parsing_utils


class TestAstParseFile:

    def test_ast_parse_file(self, dir_function, test_utils):
        filepath = test_utils.create_file(dir_function.path, 'test_file.py', content='foo = 2\n')
        ast_node = parsing_utils.ast_parse_file(filepath)
        assert isinstance(ast_node, ast.Module)


class TestTopLevelFunctions:

    def test_top_level_functions(self, dir_function, test_utils):
        path = dir_function.path

        # empty file
        filepath = test_utils.create_file(path, 'test_one.py', content='')
        ast_node = parsing_utils.ast_parse_file(filepath)
        functions = parsing_utils.top_level_functions(ast_node)
        assert functions == []

        # a python module with local functions and imported functions
        content = ('from os import listdir\n'
                   'from sys import *\n'
                   'foo = 2\n'
                   'def f1():\n'
                   '    pass\n'
                   'def f2():\n'
                   '    pass')
        filepath = test_utils.create_file(path, 'test_two.py', content=content)
        ast_node = parsing_utils.ast_parse_file(filepath)
        functions = parsing_utils.top_level_functions(ast_node)
        assert functions == ['f1', 'f2']


class TestTopLevelAssignments:

    def test_top_level_assignments(self, dir_function, test_utils):
        path = dir_function.path

        # empty file
        filepath = test_utils.create_file(path, 'test_one.py', content='')
        ast_node = parsing_utils.ast_parse_file(filepath)
        assignments = parsing_utils.top_level_assignments(ast_node)
        assert assignments == []

        # a python module with local functions and imported functions
        content = ('from os import *\n'
                   'from sys import platform\n'
                   'foo = 2\n'
                   'def f1():\n'
                   '    pass\n'
                   'bar = (1, 2, 3)\n'
                   'for n in bar:\n'
                   '    print(x)\n'
                   'if True:\n'
                   '    baz = 3')
        filepath = test_utils.create_file(path, 'test_two.py', content=content)
        ast_node = parsing_utils.ast_parse_file(filepath)
        assignments = parsing_utils.top_level_assignments(ast_node)
        assert assignments == ['foo', 'bar']
