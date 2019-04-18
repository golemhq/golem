import os
import types
import inspect

import pytest

from golem.core import utils, page_object, test_case, suite


class TestGetTestCases:

    def test_get_test_cases(self, project_class):
        _, project = project_class.activate()
        test_case.new_test_case(project, ['subdir1', 'subdir2'], 'test3')
        test_case.new_test_case(project, ['subdir1'], 'test2')
        test_case.new_test_case(project, [], 'test1')
        tests = utils.get_test_cases(project)
        expected = {
            'type': 'directory',
            'name': 'tests',
            'dot_path': '.',
            'sub_elements': [
                {
                    'type': 'directory',
                    'name': 'subdir1',
                    'dot_path': 'subdir1',
                    'sub_elements': [
                        {
                            'type': 'directory',
                            'name': 'subdir2',
                            'dot_path': 'subdir1.subdir2',
                            'sub_elements': [
                                {
                                    'type': 'file',
                                    'name': 'test3',
                                    'dot_path': 'subdir1.subdir2.test3',
                                    'sub_elements': []
                                }
                            ]
                        },
                        {
                            'type': 'file',
                            'name': 'test2',
                            'dot_path': 'subdir1.test2', 'sub_elements': []
                        }
                    ]
                },
                {
                    'type': 'file',
                    'name': 'test1',
                    'dot_path': 'test1',
                    'sub_elements': []
                }
            ]
        }
        assert tests == expected

    def test_get_test_cases_no_tests(self, project_function):
        _, project = project_function.activate()
        tests = utils.get_test_cases(project)
        expected = {'type': 'directory', 'name': 'tests', 'dot_path': '.', 'sub_elements': []}
        assert tests == expected


class TestGetPages:

    def test_get_pages(self, project_class):
        _, project = project_class.activate()
        page_object.new_page_object(project, ['subdir1', 'subdir2'], 'test3')
        page_object.new_page_object(project, ['subdir1'], 'test2')
        page_object.new_page_object(project, [], 'test1')
        pages = utils.get_pages(project)
        expected = {
            'type': 'directory',
            'name': 'pages',
            'dot_path': '.',
            'sub_elements': [
                {
                    'type': 'directory',
                    'name': 'subdir1',
                    'dot_path': 'subdir1',
                    'sub_elements': [
                        {
                            'type': 'directory',
                            'name': 'subdir2',
                            'dot_path': 'subdir1.subdir2',
                            'sub_elements': [
                            {
                                'type': 'file',
                                'name': 'test3',
                                'dot_path': 'subdir1.subdir2.test3',
                                'sub_elements': []
                            }
                        ]
                        },
                        {
                            'type': 'file',
                            'name': 'test2',
                            'dot_path': 'subdir1.test2',
                            'sub_elements': []
                        }
                    ]
                },
                {
                    'type': 'file',
                    'name': 'test1',
                    'dot_path': 'test1',
                    'sub_elements': []
                }
            ]
        }
        assert pages == expected

    def test_get_pages_no_pages(self, project_function):
        _, project = project_function.activate()
        pages = utils.get_pages(project)
        expected = {'type': 'directory', 'name': 'pages', 'dot_path': '.', 'sub_elements': []}
        assert pages == expected


class TestGetSuites:

    def test_get_suites(self, project_class):
        _, project = project_class.activate()
        suite.new_suite(project, [], 'suite1')
        suite.new_suite(project, [], 'suite2')
        suites = utils.get_suites(project)
        expected_result = {
            'type': 'directory',
            'name': 'suites',
            'dot_path': '.',
            'sub_elements': [
                {
                    'type': 'file',
                    'name': 'suite1',
                    'dot_path': 'suite1',
                    'sub_elements': []
                },
                {
                    'type': 'file',
                    'name': 'suite2',
                    'dot_path': 'suite2',
                    'sub_elements': []
                }
            ]
        }
        assert suites == expected_result

    def test_get_suites_no_suites(self, project_function):
        _, project = project_function.activate()
        suites = utils.get_suites(project)
        expected = {'type': 'directory', 'name': 'suites', 'dot_path': '.', 'sub_elements': []}
        assert suites == expected


class TestGetProjects:

    def test_get_projects(self, testdir_function):
        testdir_function.activate()
        utils.create_new_project('project1')
        utils.create_new_project('project2')
        projects = utils.get_projects()
        assert projects.sort() == ['project1', 'project2'].sort()

    def test_get_projects_no_project(self, testdir_function):
        testdir_function.activate()
        projects = utils.get_projects()
        assert projects == []


class TestGetDirectoryTests:

    def test_get_directory_test_cases(self, project_function, test_utils):
        _, project = project_function.activate()
        test_utils.create_test(project, ['foo'], 'test_one')
        test_utils.create_test(project, ['foo', 'bar'], 'test_two')
        test_utils.create_test(project, ['foo', 'bar', 'baz'], 'test_three')
        expected = ['foo.test_one', 'foo.bar.test_two', 'foo.bar.baz.test_three']
        tests = utils.get_directory_tests(project, 'foo')
        assert tests == expected
        tests = utils.get_directory_tests(project, 'foo/')
        assert tests == expected
        expected = ['foo.bar.test_two', 'foo.bar.baz.test_three']
        tests = utils.get_directory_tests(project, 'foo/bar')
        assert tests == expected


class TestCreateTestDir:

    def test_new_directory_contents(self, dir_function):
        name = 'testdirectory_001'
        os.chdir(dir_function.path)
        utils.create_test_dir(name)
        testdir = os.path.join(dir_function.path, name)
        listdir = os.listdir(testdir)
        files = [name for name in listdir if os.path.isfile(os.path.join(testdir, name))]
        dirs = [name for name in listdir if os.path.isdir(os.path.join(testdir, name))]
        if '.DS_Store' in files:
            files.remove('.DS_Store')
        assert len(files) == 3
        # verify files
        assert '__init__.py' in files
        assert 'settings.json' in files
        assert 'users.json' in files
        # verify directories
        assert len(dirs) == 2
        # verify the test dir contains the correct directories
        assert 'projects' in dirs
        assert 'drivers' in dirs


class TestDeleteElement:

    def test_delete_tests(self, project_function):
        _, project = project_function.activate()
        test_case.new_test_case(project, ['subdir1'], 'test1')
        test_case.new_test_case(project, ['subdir1'], 'test2')
        test_case.new_test_case(project, [], 'test3')
        test_case.new_test_case(project, [], 'test4')
        errors_one = utils.delete_element(project, 'test', 'subdir1.test1')
        errors_two = utils.delete_element(project, 'test', 'test3')
        assert errors_one == []
        assert errors_two == []
        path = os.path.join(project_function.path, 'tests', 'subdir1', 'test1.py')
        assert not os.path.exists(path)
        path = os.path.join(project_function.path, 'tests', 'test3.py')
        assert not os.path.exists(path)
        path = os.path.join(project_function.path, 'tests', 'subdir1', 'test2.py')
        assert os.path.exists(path)
        path = os.path.join(project_function.path, 'tests', 'test4.py')
        assert os.path.exists(path)

    def test_delete_pages(self, project_function):
        _, project = project_function.activate()
        page_object.new_page_object(project, [], 'page1')
        page_object.new_page_object(project, [], 'page2')
        errors = utils.delete_element(project, 'page', 'page1')
        assert errors == []
        path = os.path.join(project_function.path, 'pages', 'page1.py')
        assert not os.path.exists(path)
        path = os.path.join(project_function.path, 'pages', 'page2.py')
        assert os.path.exists(path)

    def test_delete_suites(self, project_function):
        _, project = project_function.activate()
        suite.new_suite(project, [], 'suite1')
        suite.new_suite(project, [], 'suite2')
        errors = utils.delete_element(project, 'suite', 'suite1')
        assert errors == []
        path = os.path.join(project_function.path, 'suites', 'suite1.py')
        assert not os.path.exists(path)
        path = os.path.join(project_function.path, 'suites', 'suite2.py')
        assert os.path.exists(path)

    def test_delete_element_does_not_exist(self, project_function):
        _, project = project_function.activate()
        errors = utils.delete_element(project, 'suite', 'suite1')
        assert errors == ['File suite1 does not exist']

    def test_delete_test_with_data(self, project_function):
        """"test that when a test is deleted the data files
        are deleted as well
        """
        _, project = project_function.activate()
        test_case.new_test_case(project, [], 'test1')
        data_path_data = os.path.join(project_function.path, 'data', 'test1.csv')
        os.makedirs(os.path.dirname(data_path_data))
        open(data_path_data, 'x').close()
        data_path_tests = os.path.join(project_function.path, 'tests', 'test1.csv')
        open(data_path_tests, 'x').close()
        errors = utils.delete_element(project, 'test', 'test1')
        assert errors == []
        test_path = os.path.join(project_function.path, 'tests', 'test1.py')
        assert not os.path.exists(test_path)
        assert not os.path.exists(data_path_data)
        assert not os.path.exists(data_path_tests)


class TestDuplicateElement:

    def test_duplicate_test(self, project_function):
        _, project = project_function.activate()
        test_case.new_test_case(project, [], 'test1')
        data_path_data = os.path.join(project_function.path, 'data', 'test1.csv')
        os.makedirs(os.path.dirname(data_path_data))
        open(data_path_data, 'x').close()
        data_path_tests = os.path.join(project_function.path, 'tests', 'test1.csv')
        open(data_path_tests, 'x').close()
        errors = utils.duplicate_element(project, 'test', 'test1', 'subdir.test2')
        assert errors == []
        path = os.path.join(project_function.path, 'tests', 'test1.py')
        assert os.path.isfile(path)
        path = os.path.join(project_function.path, 'tests', 'test1.csv')
        assert os.path.isfile(path)
        path = os.path.join(project_function.path, 'data', 'test1.csv')
        assert os.path.isfile(path)
        path = os.path.join(project_function.path, 'tests', 'subdir', 'test2.py')
        assert os.path.isfile(path)
        path = os.path.join(project_function.path, 'tests', 'subdir', 'test2.csv')
        assert os.path.isfile(path)
        path = os.path.join(project_function.path, 'data', 'subdir', 'test2.csv')
        assert os.path.isfile(path)

    def test_duplicate_page(self, project_function):
        _, project = project_function.activate()
        page_object.new_page_object(project, [], 'page1')
        errors = utils.duplicate_element(project, 'page', 'page1', 'sub.page2')
        assert errors == []
        path = os.path.join(project_function.path, 'pages', 'page1.py')
        assert os.path.isfile(path)
        path = os.path.join(project_function.path, 'pages', 'sub', 'page2.py')
        assert os.path.isfile(path)

    def test_duplicate_page_to_same_folder(self, project_function):
        _, project = project_function.activate()
        page_object.new_page_object(project, [], 'page1')
        errors = utils.duplicate_element(project, 'page', 'page1', 'page2')
        assert errors == []
        path = os.path.join(project_function.path, 'pages', 'page1.py')
        assert os.path.isfile(path)
        path = os.path.join(project_function.path, 'pages', 'page2.py')
        assert os.path.isfile(path)

    def test_duplicate_suite(self, project_function):
        _, project = project_function.activate()
        suite.new_suite(project, [], 'suite1')
        errors = utils.duplicate_element(project, 'suite', 'suite1', 'sub.suite2')
        assert errors == []
        path = os.path.join(project_function.path, 'suites', 'suite1.py')
        assert os.path.isfile(path)
        path = os.path.join(project_function.path, 'suites', 'sub', 'suite2.py')
        assert os.path.isfile(path)

    def test_duplicate_same_file(self, project_function):
        _, project = project_function.activate()
        errors = utils.duplicate_element(project, 'suite', 'suite1', 'suite1')
        assert errors == ['New file cannot be the same as the original']

    def test_duplicate_destination_already_exists(self, project_function):
        _, project = project_function.activate()
        suite.new_suite(project, [], 'suite1')
        suite.new_suite(project, [], 'suite2')
        errors = utils.duplicate_element(project, 'suite', 'suite1', 'suite2')
        assert errors == ['A file with that name already exists']


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
        result = utils.match_latest_executable_path('chromedriver*')
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
        result = utils.match_latest_executable_path('chromedriver*')
        assert result == os.path.join(basedir, 'chromedriver_2.12')

    def test_match_latest_executable_path_exe(self, dir_function, test_utils):
        """test that match_latest works for filenames ending in .exe"""
        basedir = dir_function.path
        test_utils.create_empty_file(basedir, 'chromedriver_2.4.exe')
        test_utils.create_empty_file(basedir, 'chromedriver_2.3.exe')
        test_utils.create_empty_file(basedir, 'geckodriver_5.6.7.exe')
        result = utils.match_latest_executable_path('chromedriver*')
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
        result = utils.match_latest_executable_path('./drivers/chromedriver*')
        assert result == os.path.join(path, 'chromedriver_2.4')

    def test_no_asterisk(self, dir_function, test_utils):
        """test that match_latest still works using
        no wildcards
        """
        basedir = dir_function.path
        path = os.path.join(basedir, 'drivers')
        test_utils.create_empty_file(path, 'chromedriver_2.2')
        test_utils.create_empty_file(path, 'chromedriver_2.4')
        result = utils.match_latest_executable_path('./drivers/chromedriver_2.2')
        assert result == os.path.join(path, 'chromedriver_2.2')

    def test_asterisk_subdir(self, dir_function, test_utils):
        """test that '*' wildcard can be used for dirs"""
        basedir = dir_function.path
        path = os.path.join(basedir, 'drivers')
        test_utils.create_empty_file(path, 'chromedriver_2.2')
        test_utils.create_empty_file(path, 'chromedriver_2.4')
        result = utils.match_latest_executable_path('./*/chromedriver*')
        assert result == os.path.join(path, 'chromedriver_2.4')


class TestGetValidFilename:

    filenames = [
        ('foo bar', 'foo_bar'),
        ('this is a test with "quotes"', 'this_is_a_test_with_quotes'),
        ('with %## Symbols', 'with__Symbols')
    ]

    @pytest.mark.parametrize('filename, expected', filenames)
    def test_get_valid_filename(self, filename, expected):
        result = utils.get_valid_filename(filename)
        print(filename, result)
