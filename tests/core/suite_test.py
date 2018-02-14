import os

from golem.core import suite

from tests.fixtures import (testdir_fixture,
                            permanent_project_fixture)


class Test___format_list_items:

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


class Test_save_suite:

    def test_save_suite(self, permanent_project_fixture):
        testdir = permanent_project_fixture['testdir']
        project = permanent_project_fixture['name']
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
                         workers, browsers, environments)
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
        path = os.path.join(testdir, 'projects', project, 'suites',
                            suite_name + '.py')
        with open(path) as suite_file:
            content = suite_file.read()
            assert content == expected


class Test_new_suite:

    def test_new_suite(self, permanent_project_fixture):
        testdir = permanent_project_fixture['testdir']
        project = permanent_project_fixture['name']
        suite_name = 'test_save_suite_0002'
        errors = suite.new_suite(testdir, project, [], suite_name)
        path = os.path.join(testdir, 'projects', project, 'suites',
                            suite_name + '.py')
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


    def test_new_suite_with_parents(self, permanent_project_fixture):
        testdir = permanent_project_fixture['testdir']
        project = permanent_project_fixture['name']
        suite_name = 'test_save_suite_0003'
        parents = ['asd01', 'asd02']
        errors = suite.new_suite(testdir, project, parents, suite_name)
        path = os.path.join(testdir, 'projects', project, 'suites',
                            os.sep.join(parents), suite_name + '.py')
        assert errors == []
        assert os.path.isfile(path)
        # verify that each parent dir has __init__.py file
        init_path = os.path.join(testdir, 'projects', project, 'suites',
                                 'asd01', '__init__.py')
        assert os.path.isfile(init_path)
        init_path = os.path.join(testdir, 'projects', project, 'suites',
                                 'asd01', 'asd02', '__init__.py')
        assert os.path.isfile(init_path)


    def test_new_suite_already_exists(self, permanent_project_fixture):
        testdir = permanent_project_fixture['testdir']
        project = permanent_project_fixture['name']
        suite_name = 'test_save_suite_0003'
        suite.new_suite(testdir, project, [], suite_name)
        errors = suite.new_suite(testdir, project, [], suite_name)
        assert errors == ['A suite with that name already exists']


    def test_new_suite_with_parents_already_exist(self, permanent_project_fixture):
        testdir = permanent_project_fixture['testdir']
        project = permanent_project_fixture['name']
        suite_name1 = 'test_save_suite_0004'
        suite_name2 = 'test_save_suite_0005'
        parents = ['asf01']
        suite.new_suite(testdir, project, parents, suite_name1)
        errors = suite.new_suite(testdir, project, parents, suite_name2)
        path = os.path.join(testdir, 'projects', project, 'suites',
                            os.sep.join(parents), suite_name2 + '.py')
        assert errors == []
        assert os.path.isfile(path)
