import os

from golem.core import suite
from golem.core.suite import Suite
from golem.core.project import Project


class TestCreateSuite:

    def test_create_suite(self, project_session, test_utils):
        _, project = project_session.activate()
        suite_name = test_utils.random_string()
        errors = suite.create_suite(project, suite_name)
        assert errors == []
        assert suite_name in Project(project).suites()
        # verify new suite content
        with open(Suite(project, suite_name).path) as f:
            content = f.read()
            expected = ('\n'
                        'browsers = []\n\n'
                        'environments = []\n\n'
                        'processes = 1\n\n'
                        'tests = []\n')
            assert content == expected

    def test_create_suite_with_parents(self, project_session, test_utils):
        _, project = project_session.activate()
        random_name = test_utils.random_string()
        parents = [test_utils.random_string(), test_utils.random_string()]
        suite_name = '{}.{}.{}'.format(parents[0], parents[1], random_name)
        errors = suite.create_suite(project, suite_name)
        assert errors == []
        assert os.path.isfile(Suite(project, suite_name).path)
        # verify that each parent dir has __init__.py file
        init_path = os.path.join(Project(project).suite_directory_path, parents[0], '__init__.py')
        assert os.path.isfile(init_path)
        init_path = os.path.join(Project(project).suite_directory_path, parents[0], parents[1], '__init__.py')
        assert os.path.isfile(init_path)

    def test_create_suite_already_exists(self, project_session, test_utils):
        _, project = project_session.activate()
        suite_name = test_utils.create_random_suite(project)
        errors = suite.create_suite(project, suite_name)
        assert errors == ['A suite with that name already exists']

    def test_create_suite_invalid_name(self, project_session):
        _, project = project_session.activate()
        errors = suite.create_suite(project, 'invalid-name')
        assert errors == ['Only letters, numbers and underscores are allowed']
        errors = suite.create_suite(project, 'suite.')
        assert errors == ['File name cannot be empty']
        errors = suite.create_suite(project, '.suite')
        assert errors == ['Directory name cannot be empty']


class TestRenameSuite:

    def test_rename_suite(self, project_session, test_utils):
        _, project = project_session.activate()
        suite_name = test_utils.create_random_suite(project)
        new_suite_name = test_utils.random_string()
        suite.rename_suite(project, suite_name, new_suite_name)
        suites = Project(project).suites()
        assert suite_name not in suites
        assert new_suite_name in suites

    def test_rename_suite_to_new_directory(self, project_session, test_utils):
        _, project = project_session.activate()
        suite_name = test_utils.create_random_suite(project)
        random_dir = test_utils.random_string()
        new_suite_name = '{}.{}'.format(random_dir, test_utils.random_string())
        suite.rename_suite(project, suite_name, new_suite_name)
        suites = Project(project).suites()
        assert suite_name not in suites
        assert new_suite_name in suites
        init_path = os.path.join(Project(project).suite_directory_path, random_dir, '__init__.py')
        assert os.path.isfile(init_path)


class TestDuplicateSuite:

    def test_duplicate_suite(self, project_session, test_utils):
        _, project = project_session.activate()
        suite_name = test_utils.create_random_suite(project)
        new_suite_name = test_utils.random_string()
        errors = suite.duplicate_suite(project, suite_name, new_suite_name)
        assert errors == []
        suites = Project(project).suites()
        assert suite_name in suites
        assert new_suite_name in suites

    def test_duplicate_suite_same_name(self, project_session, test_utils):
        _, project = project_session.activate()
        suite_name = test_utils.create_random_suite(project)
        errors = suite.duplicate_suite(project, suite_name, suite_name)
        assert errors == ['New suite name cannot be the same as the original']

    def test_duplicate_suite_name_already_exists(self, project_session, test_utils):
        _, project = project_session.activate()
        suite_name = test_utils.create_random_suite(project)
        suite_name_two = test_utils.create_random_suite(project)
        errors = suite.duplicate_suite(project, suite_name, suite_name_two)
        assert errors == ['A suite with that name already exists']

    def test_duplicate_suite_invalid_name(self, project_session, test_utils):
        _, project = project_session.activate()
        suite_name = test_utils.create_random_suite(project)
        new_suite_name = 'new-name'
        errors = suite.duplicate_suite(project, suite_name, new_suite_name)
        assert errors == ['Only letters, numbers and underscores are allowed']


class TestEditSuite:

    def test_edit_suite(self, project_session, test_utils):
        _, project = project_session.activate()
        suite_name = test_utils.create_random_suite(project)
        tests = [
            'test01',
            'test02'
        ]
        browsers = [
            'browser01',
            'browser02',
        ]
        processes = 2
        environments = [
            'env01',
            'env02'
        ]
        suite.edit_suite(project, suite_name, tests, processes, browsers, environments, [])
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
            "processes = 2\n"
            "\n"
            "tests = [\n"
            "    'test01',\n"
            "    'test02'\n"
            "]\n"
        )
        with open(Suite(project, suite_name).path) as f:
            assert f.read() == expected

    def test_edit_suite_empty(self, project_session, test_utils):
        _, project = project_session.activate()
        suite_name = test_utils.create_random_suite(project)
        tests = []
        browsers = []
        processes = 2
        environments = []
        suite.edit_suite(project, suite_name, tests, processes, browsers, environments, [])
        expected = (
            "\n"
            "\n"
            "browsers = []\n"
            "\n"
            "environments = []\n"
            "\n"
            "processes = 2\n"
            "\n"
            "tests = []\n"
        )
        with open(Suite(project, suite_name).path) as f:
            assert f.read() == expected


class TestDeleteSuite:

    def test_delete_suite(self, project_session, test_utils):
        _, project = project_session.activate()
        suite_name = test_utils.create_random_suite(project)
        errors = suite.delete_suite(project, suite_name)
        assert errors == []
        assert suite_name not in Project(project).suites()

    def test_delete_suite_not_exist(self, project_session):
        _, project = project_session.activate()
        errors = suite.delete_suite(project, 'not-exist')
        assert errors == ['Suite not-exist does not exist']


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


class TestSuiteProcesses:

    def test_suite_processes(self, project_session, test_utils):
        _, project = project_session.activate()
        suite_name = test_utils.create_random_suite(project)
        assert Suite(project, suite_name).processes == 1
        processes = 2
        suite.edit_suite(project, suite_name, [], processes, [], [], [])
        assert Suite(project, suite_name).processes == processes


class TestSuiteEnvironments:

    def test_suite_environments(self, project_session, test_utils):
        _, project = project_session.activate()
        suite_name = test_utils.create_random_suite(project)
        assert Suite(project, suite_name).environments == []
        environments = ['env1', 'env2']
        suite.edit_suite(project, suite_name, [], 1, [], environments, [])
        assert Suite(project, suite_name).environments == environments


class TestSuiteBrowsers:

    def test_suite_browsers(self, project_session, test_utils):
        _, project = project_session.activate()
        suite_name = test_utils.create_random_suite(project)
        assert Suite(project, suite_name).browsers == []
        browsers = ['browser1', 'browser2']
        suite.edit_suite(project, suite_name, [], 1, browsers, [], [])
        assert Suite(project, suite_name).browsers == browsers


class TestSuiteTests:

    def test_suite_tests(self, project_function, test_utils):
        _, project = project_function.activate()
        suite_name = test_utils.create_random_suite(project)
        test_utils.create_test(project, 'test1')
        test_utils.create_test(project, 'test2')
        tests = ['test1', 'test2']
        suite.edit_suite(project, suite_name, tests, 1, [], [], [])
        assert Suite(project, suite_name).tests == tests

        test_utils.create_test(project, 'dir.test3')
        test_utils.create_test(project, 'dir.subdir.test4')
        tests = ['test1', 'test2', 'dir.test3', 'dir.subdir.test4']
        suite.edit_suite(project, suite_name, tests, 1, [], [], [])
        assert Suite(project, suite_name).tests == tests

        tests = ['test1', 'test2', 'dir.*']
        suite.edit_suite(project, suite_name, tests, 1, [], [], [])
        expected = ['test1', 'test2', 'dir.test3', 'dir.subdir.test4']
        assert Suite(project, suite_name).tests == expected

    def test_suite_tests_asterisk(self, project_function, test_utils):
        _, project = project_function.activate()
        test_utils.create_test(project, 'test01')
        test_utils.create_test(project, 'a.b.test02')
        suite_name = test_utils.create_random_suite(project)
        tests = ['*']
        suite.edit_suite(project, suite_name, tests, 1, [], [], [])
        assert Suite(project, suite_name).tests == ['test01', 'a.b.test02']
