import os
import types

from golem.core import suite, test_case


class TestFormatListItems:

    def test___format_list_items(self):
        input_list = ['a', 'b']
        output = suite._format_list_items(input_list)
        expected = "[\n    'a',\n    'b'\n]"
        assert output == expected

    def test___format_list_items_one_item(self):
        input_list = ['a']
        output = suite._format_list_items(input_list)
        expected = "[\n    'a'\n]"
        assert output == expected

    def test___format_list_items_empty_list(self):
        input_list = []
        output = suite._format_list_items(input_list)
        expected = "[]"
        assert output == expected


class TestSaveSuite:

    def test_save_suite(self, project_session):
        testdir = project_session.testdir
        project = project_session.name
        suite_name = 'test_save_suite_0001'
        suite.new_suite(testdir, project, [], suite_name)
        test_cases = [
            'test01',
            'test02'
        ]
        browsers = [
            'browser01',
            'browser02',
        ]
        workers = 2
        environments = [
            'env01',
            'env02'
        ]
        suite.save_suite(testdir, project, suite_name, test_cases,
                         workers, browsers, environments, [])
        expected = (
            "\n"
            "\n"
            "browsers = [\n"
            "    'browser01',\n"
            "    'browser02'\n"
            "]\n"
            "\n"
            "environments = [\n"
            "    'env01',\n"
            "    'env02'\n"
            "]\n"
            "\n"
            "workers = 2\n"
            "\n"
            "tests = [\n"
            "    'test01',\n"
            "    'test02'\n"
            "]\n"
        )
        path = os.path.join(project_session.path, 'suites', suite_name + '.py')
        with open(path) as suite_file:
            content = suite_file.read()
            assert content == expected

    def test_save_suite_empty(self, project_session):
        testdir = project_session.testdir
        project = project_session.name
        suite_name = 'test_save_suite_0002'
        suite.new_suite(testdir, project, [], suite_name)
        test_cases = []
        browsers = []
        workers = 2
        environments = []
        suite.save_suite(testdir, project, suite_name, test_cases,
                         workers, browsers, environments, [])
        expected = (
            "\n"
            "\n"
            "browsers = []\n"
            "\n"
            "environments = []\n"
            "\n"
            "workers = 2\n"
            "\n"
            "tests = []\n"
        )
        path = os.path.join(project_session.path, 'suites', suite_name + '.py')
        with open(path) as suite_file:
            content = suite_file.read()
            assert content == expected


class TestNewSuite:

    def test_new_suite(self, project_session):
        testdir = project_session.testdir
        project = project_session.name
        suite_name = 'test_save_suite_0003'
        errors = suite.new_suite(testdir, project, [], suite_name)
        path = os.path.join(project_session.path, 'suites', suite_name + '.py')
        assert errors == []
        assert os.path.isfile(path)
        # verify new suite content
        with open(path) as suite_file:
            content = suite_file.read()
            expected = ('\n'
                        'browsers = []\n\n'
                        'environments = []\n\n'
                        'workers = 1\n\n'
                        'tests = []\n')
            assert content == expected

    def test_new_suite_with_parents(self, project_session):
        testdir = project_session.testdir
        project = project_session.name
        suite_name = 'test_save_suite_004'
        parents = ['asd01', 'asd02']
        errors = suite.new_suite(testdir, project, parents, suite_name)
        path = os.path.join(project_session.path, 'suites',
                            os.sep.join(parents), suite_name + '.py')
        assert errors == []
        assert os.path.isfile(path)
        # verify that each parent dir has __init__.py file
        init_path = os.path.join(project_session.path, 'suites', 'asd01', '__init__.py')
        assert os.path.isfile(init_path)
        init_path = os.path.join(project_session.path, 'suites', 'asd01', 'asd02', '__init__.py')
        assert os.path.isfile(init_path)

    def test_new_suite_already_exists(self, project_session):
        testdir = project_session.testdir
        project = project_session.name
        suite_name = 'test_save_suite_0005'
        suite.new_suite(testdir, project, [], suite_name)
        errors = suite.new_suite(testdir, project, [], suite_name)
        assert errors == ['a suite with that name already exists']

    def test_new_suite_with_parents_already_exist(self, project_session):
        testdir = project_session.testdir
        project = project_session.name
        suite_name1 = 'test_save_suite_0006'
        suite_name2 = 'test_save_suite_0007'
        parents = ['asf01']
        suite.new_suite(testdir, project, parents, suite_name1)
        errors = suite.new_suite(testdir, project, parents, suite_name2)
        path = os.path.join(project_session.path, 'suites',
                            os.sep.join(parents), suite_name2 + '.py')
        assert errors == []
        assert os.path.isfile(path)


class TestGetSuiteAmountOfWorkers:

    def test_get_suite_amount_of_workers(self, project_function):
        testdir = project_function.testdir
        project = project_function.name
        suite_name = 'test_suite_workers_001'
        suite.new_suite(testdir, project, [], suite_name)
        worker_amount = 2
        suite.save_suite(testdir, project, suite_name, [], worker_amount, [], [], [])
        workers = suite.get_suite_amount_of_workers(testdir, project, suite_name)
        assert workers == worker_amount


class TestGetSuiteEnvironments:

    def test_get_suite_environments(self, project_function):
        testdir = project_function.testdir
        project = project_function.name
        suite_name = 'test_suite_002'
        suite.new_suite(testdir, project, [], suite_name)
        environments = ['env1', 'env2']
        suite.save_suite(testdir, project, suite_name, [], 1, [], environments, [])
        result = suite.get_suite_environments(testdir, project, suite_name)
        assert result == environments


class TestGetSuiteTestCases:

    def test_get_suite_test_cases(self, project_function):
        testdir = project_function.testdir
        project = project_function.name
        suite_name = 'test_suite_003'
        suite.new_suite(testdir, project, [], suite_name)
        tests = ['test_name_01', 'test_name_02']
        suite.save_suite(testdir, project, suite_name, tests, 1, [], [], [])
        result = suite.get_suite_test_cases(testdir, project, suite_name)
        assert result == tests

    def test_get_suite_test_cases_get_all(self, project_function):
        testdir = project_function.testdir
        project = project_function.name
        test_case.new_test_case(testdir, project, [], 'test_name_01')
        test_case.new_test_case(testdir, project, ['a', 'b'], 'test_name_02')
        suite_name = 'test_suite_004'
        suite.new_suite(testdir, project, [], suite_name)
        tests = ['*']
        suite.save_suite(testdir, project, suite_name, tests, 1, [], [], [])
        result = suite.get_suite_test_cases(testdir, project, suite_name)
        expected = ['test_name_01', 'a.b.test_name_02']
        assert result == expected


class TestGetSuiteBrowsers:

    def test_get_suite_browsers(self, project_function):
        testdir = project_function.testdir
        project = project_function.name
        suite_name = 'test_suite_005'
        suite.new_suite(testdir, project, [], suite_name)
        browsers = ['browser1', 'browser2']
        suite.save_suite(testdir, project, suite_name, [], 1, browsers, [], [])
        result = suite.get_suite_browsers(testdir, project, suite_name)
        assert result == browsers


class TestGetSuiteModule:

    def test_get_suite_module(self, project_function):
        testdir = project_function.testdir
        project = project_function.name
        suite_name = 'test_suite_006'
        suite.new_suite(testdir, project, [], suite_name)
        module = suite.get_suite_module(testdir, project, suite_name)
        assert isinstance(module, types.ModuleType)

    def test_get_suite_module_does_not_exist(self, project_function):
        testdir = project_function.testdir
        project = project_function.name
        suite_name = 'test_suite_007'
        module = suite.get_suite_module(testdir, project, suite_name)
        assert module is None
