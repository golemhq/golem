import os

from golem.core import tags_manager


class TestGetTestsTags:

    def test_get_tests_tags(self, project_function, test_utils):
        testdir = project_function.testdir
        project = project_function.name
        # empty test list
        tags = tags_manager.get_tests_tags(testdir, project, [])
        assert tags == {}
        content = 'tags = ["foo", "bar"]'
        test_utils.create_test(testdir, project, parents=[], name='test_tags_001', content=content)
        # test tags for one test
        tags = tags_manager.get_tests_tags(testdir, project, ['test_tags_001'])
        assert tags == {'test_tags_001': ["foo", "bar"]}
        # test without tags returns empty list
        test_utils.create_test(testdir, project, parents=[], name='test_tags_002')
        tags = tags_manager.get_tests_tags(testdir, project, ['test_tags_001', 'test_tags_002'])
        assert tags['test_tags_002'] == []

    def test_get_tests_tags_verify_cache(self, project_function, test_utils):
        testdir = project_function.testdir
        project = project_function.name
        test_name = 'test_tags_003'
        content = 'tags = ["foo", "bar"]'
        test_path = test_utils.create_test(testdir, project, parents=[], name=test_name,
                                           content=content)
        # verify cache file does not exist and is created afterwards
        cache_path = os.path.join(testdir, 'projects', project, '.tags')
        assert not os.path.isfile(cache_path)
        tags = tags_manager.get_tests_tags(testdir, project, [test_name])
        assert os.path.isfile(cache_path)
        assert tags[test_name] == ["foo", "bar"]
        # verify that when a test is updated, the cache is updated as well
        last_modified_time = os.path.getmtime(cache_path)
        content = 'tags = ["baz"]'
        with open(test_path, 'w') as f:
            f.write(content)
        tags = tags_manager.get_tests_tags(testdir, project, [test_name])
        assert os.path.getmtime(cache_path) > last_modified_time
        assert tags[test_name] == ['baz']


class TestGetAllProjectTestsTags:

    def test_get_all_project_tests_tags(self, project_function, test_utils):
        testdir = project_function.testdir
        project = project_function.name
        # no tests
        tags = tags_manager.get_all_project_tests_tags(testdir, project)
        assert tags == {}
        # with tests
        content = 'tags = ["foo", "bar"]'
        test_utils.create_test(testdir, project, parents=[], name='test001', content=content)
        content = 'tags = ["001", "002"]'
        test_utils.create_test(testdir, project, parents=[], name='test002', content=content)
        tags = tags_manager.get_all_project_tests_tags(testdir, project)
        assert tags == {'test001': ['foo', 'bar'], 'test002': ['001', '002']}


class TestGetProjectUniqueTags:

    def test_get_project_unique_tags(self, project_function, test_utils):
        testdir = project_function.testdir
        project = project_function.name
        content = 'tags = ["foo", "bar"]'
        test_utils.create_test(testdir, project, parents=[], name='test001', content=content)
        content = 'tags = ["bar", "baz"]'
        test_utils.create_test(testdir, project, parents=[], name='test002', content=content)
        tags = tags_manager.get_project_unique_tags(testdir, project)
        assert sorted(tags) == sorted(['foo', 'bar', 'baz'])
