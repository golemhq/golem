import os
import types
import inspect

import pytest

from golem.core import utils
from golem.core.page import Page


class TestChooseBrowserByPrecedence:

    def test_choose_browser_by_precedence(self):
        selected = utils.choose_browser_by_precedence(cli_browsers=['a', 'b'],
                                                      suite_browsers=['c', 'd'],
                                                      settings_default_browser='default')
        assert selected == ['a', 'b']
        selected = utils.choose_browser_by_precedence(cli_browsers=[],
                                                      suite_browsers=['c', 'd'],
                                                      settings_default_browser='default')
        assert selected == ['c', 'd']
        selected = utils.choose_browser_by_precedence(cli_browsers=[],
                                                      suite_browsers=[],
                                                      settings_default_browser='default')
        assert selected == ['default']
        selected = utils.choose_browser_by_precedence(cli_browsers=[],
                                                      suite_browsers=[],
                                                      settings_default_browser=None)
        assert selected == ['chrome']


class TestImportModule:

    def test_import_module_success(self, dir_function):
        filename = 'python_module.py'
        filepath = os.path.join(dir_function.path, filename)
        filecontent = ('foo = 2\n'
                       'def bar(a, b):\n'
                       '    baz = ""\n')
        with open(filepath, 'w') as f:
            f.write(filecontent)
        module, error = utils.import_module(filepath)
        assert isinstance(module, types.ModuleType)
        assert error is None
        foo = getattr(module, 'foo')
        assert type(foo) == int
        bar = getattr(module, 'bar')
        assert isinstance(bar, types.FunctionType)
        args = list(inspect.signature(bar).parameters)
        code = inspect.getsource(bar)
        assert args == ['a', 'b']
        assert code == 'def bar(a, b):\n    baz = ""\n'

    def test_module_does_not_exist(self, dir_function):
        filepath = os.path.join(dir_function.path, 'non_existent.py')
        module, error = utils.import_module(filepath)
        assert module is None

    syntax_tests = [
        (
            ('var = 2 +\n'),
            ('    var = 2 +\n'
             '            ^\n'
             'SyntaxError: invalid syntax\n')
        ),
        (
            ('import\n'
             'var = 2 + 2'),
            ('    import\n'
             '         ^\n'
             'SyntaxError: invalid syntax\n')
        ),
        (
            ('def func()\n'
             '    var = 2 + 2\n'),
            ('    def func()\n'
             '             ^\n'
             'SyntaxError: invalid syntax\n')
        ),
        (
            'data = [{"key": unknown}]',
            "NameError: name 'unknown' is not defined"
        ),
    ]

    @pytest.mark.parametrize('filecontent, expected', syntax_tests)
    def test_incorrect_syntax(self, filecontent, expected, dir_function):
        filename = 'test_python_syntax.py'
        filepath = os.path.join(dir_function.path, filename)
        with open(filepath, 'w') as f:
            f.write(filecontent)
        _, error = utils.import_module(filepath)
        assert expected in error


class TestModuleLocalFunctions:

    def test_module_local_functions(self):
        """module imported using import statement"""
        from golem import actions
        functions = utils.module_local_public_functions(actions)
        dir_actions = dir(actions)
        # not in functions
        assert 'contextmanager' in dir_actions and 'contextmanager' not in functions
        assert 'code' in dir_actions and 'code' not in functions
        assert '_add_error' in dir_actions and '_add_error' not in functions
        # in functions
        assert 'accept_alert' in dir_actions and 'accept_alert' in functions
        assert 'wait_for_window_present_by_url' in dir_actions and 'wait_for_window_present_by_url' in functions

    def test_module_local_functions_programatically(self, project_session, test_utils):
        """module imported from path"""
        _, project = project_session.activate()
        page_code = ('import sys\n'
                     'from os import walk\n'
                     'foo = 1\n'
                     'def bar():\n'
                     '  pass\n'
                     'def _baz():\n'
                     '  pass\n'
                     'class Traz:\n'
                     '  pass')
        page_name = test_utils.create_random_page(project, page_code)
        module, _ = utils.import_module(Page(project, page_name).path)
        functions = utils.module_local_public_functions(module)
        assert len(functions) == 1
        assert 'sys' not in functions
        assert 'walk' not in functions
        assert 'foo' not in functions
        assert '_baz' not in functions
        assert 'Traz' not in functions
        assert 'bar' in functions


class TestExtractVersionFromWebDriverFilename:

    filenames = [
        ('chromedriver_2.3', '2.3'),
        ('chromedriver_2.3.4', '2.3.4'),
        ('chromedriver_2.3.exe', '2.3'),
        ('chromedriver-no-version', '0.0'),
        ('invalid_2a.3', '0.0'),
        ('invalid_test', '0.0'),
        ('chromedriver_test_2.3', '2.3'),
    ]

    @pytest.mark.parametrize('filename, expected', filenames)
    def test_extract_version_from_filename(self, filename, expected):
        result = utils.extract_version_from_webdriver_filename(filename)
        assert result == expected


class TestMatchLatestExecutablePath:

    def test_match_latest_executable_path(self, dir_function, test_utils):
        """the latest version filepath matching glob pattern
        is returned
        """
        basedir = dir_function.path
        test_utils.create_empty_file(basedir, 'chromedriver_2.2')
        test_utils.create_empty_file(basedir, 'chromedriver_2.4')
        test_utils.create_empty_file(basedir, 'chromedriver_2.3')
        test_utils.create_empty_file(basedir, 'geckodriver_5.6.7')
        result = utils.match_latest_executable_path('chromedriver*', basedir)
        assert result == os.path.join(basedir, 'chromedriver_2.4')

    def test_match_latest_executable_path__compare_versions_not_strings(self, dir_function,
                                                                        test_utils):
        """2.12 should be higher than 2.9
        (but it's when not comparing just strings)
        e.g. '2.9' > '2.12'
        """
        basedir = dir_function.path
        test_utils.create_empty_file(basedir, 'chromedriver_2.9')
        test_utils.create_empty_file(basedir, 'chromedriver_2.12')
        result = utils.match_latest_executable_path('chromedriver*', basedir)
        assert result == os.path.join(basedir, 'chromedriver_2.12')

    def test_match_latest_executable_path_exe(self, dir_function, test_utils):
        """test that match_latest works for filenames ending in .exe"""
        basedir = dir_function.path
        test_utils.create_empty_file(basedir, 'chromedriver_2.4.exe')
        test_utils.create_empty_file(basedir, 'chromedriver_2.3.exe')
        test_utils.create_empty_file(basedir, 'geckodriver_5.6.7.exe')
        result = utils.match_latest_executable_path('chromedriver*', basedir)
        assert result == os.path.join(basedir, 'chromedriver_2.4.exe')

    def test_match_latest_executable_path_subdir(self, dir_function, test_utils):
        """test that match_latest works passing a rel path
        to a subdir
        """
        basedir = dir_function.path
        path = os.path.join(basedir, 'drivers')
        test_utils.create_empty_file(path, 'chromedriver_2.2')
        test_utils.create_empty_file(path, 'chromedriver_2.4')
        test_utils.create_empty_file(path, 'chromedriver_2.3')
        test_utils.create_empty_file(path, 'geckodriver_5.6.7')
        result = utils.match_latest_executable_path('./drivers/chromedriver*', basedir)
        assert result == os.path.join(path, 'chromedriver_2.4')

    def test_no_asterisk(self, dir_function, test_utils):
        """test that match_latest still works using
        no wildcards
        """
        basedir = dir_function.path
        path = os.path.join(basedir, 'drivers')
        test_utils.create_empty_file(path, 'chromedriver_2.2')
        test_utils.create_empty_file(path, 'chromedriver_2.4')
        result = utils.match_latest_executable_path('./drivers/chromedriver_2.2', basedir)
        assert result == os.path.join(path, 'chromedriver_2.2')

    def test_asterisk_subdir(self, dir_function, test_utils):
        """test that '*' wildcard can be used for dirs"""
        basedir = dir_function.path
        path = os.path.join(basedir, 'drivers')
        test_utils.create_empty_file(path, 'chromedriver_2.2')
        test_utils.create_empty_file(path, 'chromedriver_2.4')
        result = utils.match_latest_executable_path('./*/chromedriver*', basedir)
        assert result == os.path.join(path, 'chromedriver_2.4')

    def test_match_latest_executable_path__absolute_path(self, dir_function, test_utils):
        """an absolute path can be passed"""
        basedir = dir_function.path
        test_utils.create_empty_file(basedir, 'chromedriver_2.2')
        test_utils.create_empty_file(basedir, 'chromedriver_2.3')
        abspath = os.path.join(os.path.abspath(basedir), 'chromedriver_2.3')
        result = utils.match_latest_executable_path(abspath, basedir)
        assert result == os.path.join(basedir, 'chromedriver_2.3')

    def test_match_latest_executable_path__no_match(self, dir_function):
        result = utils.match_latest_executable_path(dir_function.path, dir_function.path)
        assert result is None


class TestGetValidFilename:

    filenames = [
        ('foo bar', 'foo_bar'),
        ('this is a test with "quotes"', 'this_is_a_test_with_quotes'),
        ('with %## Symbols', 'with__Symbols')
    ]

    @pytest.mark.parametrize('filename, expected', filenames)
    def test_get_valid_filename(self, filename, expected):
        result = utils.get_valid_filename(filename)
        assert result == expected


class TestNormalizeQuery:

    queries = [
        ('test', 'test'),
        ('suite.py', 'suite'),
        ('suite', 'suite'),
        ('folder.suite', 'folder.suite'),
        ('folder/suite.py', 'folder.suite')
    ]

    @pytest.mark.parametrize('query, normalized', queries)
    def test_normalize_query(self, query, normalized):
        assert utils.normalize_query(query) == normalized

    @pytest.mark.skipif("os.name != 'nt'")
    def test_normalize_query_windows(self):
        assert utils.normalize_query('folder\\suite.py') == 'folder.suite'
