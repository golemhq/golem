import json
import os

from golem.core import test_data
from golem.core import test


class TestSaveCSVTestData:

    def test_save_csv_data(self, project_class, test_utils):
        _, project = project_class.activate()
        test_name = test_utils.random_string()
        input_test_data = [{'key1': 'value1', 'key2': 'value2'},
                           {'key1': 'value3', 'key2': 'value4'}]
        test_data.save_csv_test_data(project, test_name, input_test_data)
        with open(test_data.csv_file_path(project, test_name)) as f:
            result = f.read()
            expected = ('key1,key2\n'
                        'value1,value2\n'
                        'value3,value4\n')
            assert result == expected

    def test_save_csv_data_empty_data(self, project_class, test_utils):
        _, project = project_class.activate()
        test_name = test_utils.random_string()
        input_test_data = []
        test_data.save_csv_test_data(project, test_name, input_test_data)
        assert not os.path.isfile(test_data.csv_file_path(project, test_name))

    def test_save_csv_data_empty_data_file_exists(self, project_class, test_utils):
        """csv file is removed when data is empty"""
        _, project = project_class.activate()
        test_name = test_utils.random_string()
        input_test_data = []
        data_path = test_data.csv_file_path(project, test_name)
        open(data_path, 'w+').close()
        test_data.save_csv_test_data(project, test_name, input_test_data)
        assert not os.path.isfile(data_path)

    def test_save_csv_data_special_cases(self, project_class, test_utils):
        _, project = project_class.activate()
        test_name = test_utils.random_string()
        input_test_data = [{'key1': 'string with spaces'},
                           {'key1': 'string "with" quotes'},
                           {'key1': 'string \'with\' quotes'},
                           {'key1': '"quoted_string"'},
                           {'key1': '\'quoted_string\''}]
        test_data.save_csv_test_data(project, test_name, input_test_data)
        with open(test_data.csv_file_path(project, test_name)) as f:
            result = f.read()
            expected = ('key1\n'
                        'string with spaces\n'
                        '"string ""with"" quotes"\n'
                        'string \'with\' quotes\n'
                        '"""quoted_string"""\n'
                        '\'quoted_string\'\n')
            assert result == expected


class TestGetCSVTestData:

    def test_get_csv_test_data(self, project_class, test_utils):
        _, project = project_class.activate()
        test_name = test_utils.random_string()
        input = 'key1,key2\nvalue1,value2\nvalue3,value4\n'
        with open(test_data.csv_file_path(project, test_name), 'w+') as f:
            f.write(input)
        result = test_data.get_csv_test_data(project, test_name)
        expected = [{'key1': 'value1', 'key2': 'value2'},
                    {'key1': 'value3', 'key2': 'value4'}]
        assert result == expected

    def test_get_csv_test_data_no_file(self, project_class, test_utils):
        _, project = project_class.activate()
        test_name = test_utils.random_string()
        result = test_data.get_csv_test_data(project, test_name)
        assert result == []

    def test_get_csv_test_data_special_cases(self, project_class, test_utils):
        _, project = project_class.activate()
        test_name = test_utils.random_string()
        input = ('key1\n'
                 'string with spaces\n'
                 '"string ""with"" quotes"\n'
                 'string \'with\' quotes\n'
                 '"""quoted_string"""\n'
                 '\'quoted_string\'\n')
        with open(test_data.csv_file_path(project, test_name), 'w+') as f:
            f.write(input)
        result = test_data.get_csv_test_data(project, test_name)
        expected = [{'key1': 'string with spaces'},
                    {'key1': 'string "with" quotes'},
                    {'key1': 'string \'with\' quotes'},
                    {'key1': '"quoted_string"'},
                    {'key1': '\'quoted_string\''}]
        assert result == expected


class TestSaveJsonTestData:

    def test_save_json_data(self, project_class, test_utils):
        _, project = project_class.activate()
        test_name = test_utils.random_string()
        json_data_str = '[{"foo": "bar"}]'
        test_data.save_json_test_data(project, test_name, json_data_str)
        json_data = test_data.get_json_test_data(project, test_name)
        assert json_data == [{'foo': 'bar'}]

    def test_save_json_data_empty_data(self, project_class, test_utils):
        _, project = project_class.activate()
        test_name = test_utils.random_string()
        test_data.save_csv_test_data(project, test_name, '')
        assert not os.path.isfile(test_data.json_file_path(project, test_name))

    def test_save_json_data_invalid_json(self, project_class, test_utils):
        _, project = project_class.activate()
        test_name = test_utils.random_string()
        json_data_str = '[{"foo": "bar"]'
        test_data.save_json_test_data(project, test_name, json_data_str)
        assert not os.path.isfile(test_data.json_file_path(project, test_name))


class TestGetJsonTestData:

    def test_get_json_data_is_dict(self, project_class, test_utils):
        """json dict is return as a list of dict"""
        _, project = project_class.activate()
        test_name = test_utils.random_string()
        json_data_str = '{"foo": "bar"}'
        test_data.save_json_test_data(project, test_name, json_data_str)
        json_data = test_data.get_json_test_data(project, test_name)
        assert json_data == [{'foo': 'bar'}]

    def test_get_json_data_list_of_dicts(self, project_class, test_utils):
        """json dict is return as a list of dict"""
        _, project = project_class.activate()
        test_name = test_utils.random_string()
        json_data_str = '[{"foo": "bar"}, {"foo": "etc"}]'
        test_data.save_json_test_data(project, test_name, json_data_str)
        json_data = test_data.get_json_test_data(project, test_name)
        assert json_data == [{'foo': 'bar'}, {'foo': 'etc'}]

    def test_get_json_data_list_of_not_dicts(self, project_class, test_utils):
        """an element in the list is not a dict"""
        _, project = project_class.activate()
        test_name = test_utils.random_string()
        json_data_str = '[{"foo": "bar"}, "not a dict"]'
        test_data.save_json_test_data(project, test_name, json_data_str)
        json_data = test_data.get_json_test_data(project, test_name)
        assert json_data == []

    def test_get_json_data_not_list_not_dict(self, project_class, test_utils):
        """not a list and not a dict"""
        _, project = project_class.activate()
        test_name = test_utils.random_string()
        json_data_str = '"not a dict"'
        test_data.save_json_test_data(project, test_name, json_data_str)
        json_data = test_data.get_json_test_data(project, test_name)
        assert json_data == []


class TestGetJsonTestDataAsString:

    def test_get_json_data_as_string(self, project_class, test_utils):
        _, project = project_class.activate()
        test_name = test_utils.random_string()
        json_data_str = '{"foo": "bar"}'
        test_data.save_json_test_data(project, test_name, json_data_str)
        json_data = test_data.get_json_test_data_as_string(project, test_name)
        assert json_data == '{"foo": "bar"}'

    def test_get_json_data_as_string_no_file(self, project_class, test_utils):
        _, project = project_class.activate()
        test_name = test_utils.random_string()
        json_data = test_data.get_json_test_data_as_string(project, test_name)
        assert json_data == ''


class TestValidateInternalData:

    def test_validate_internal_data(self):
        result = test_data.validate_internal_data('data = [{"foo": "bar"}]')
        assert result == []

    def test_validate_internal_data_invalid(self):
        result = test_data.validate_internal_data('data = [{"foo": "bar"]')
        assert '^\nSyntaxError: invalid syntax\n' in result[0]
        assert len(result) == 1


class TestGetInternalTestDataAsString:

    def test_get_internal_data_as_string(self, project_class, test_utils):
        _, project = project_class.activate()
        test_name = test_utils.create_random_test(project)
        test_content = ("data = [\n"
                        "    {'key1': 'a'},\n"
                        "    {'key1': 'b'},\n"
                        "]\n"
                        "def test(data):\n"
                        "    pass\n")
        with open(test.Test(project, test_name).path, 'w+') as f:
            f.write(test_content)
        data_str = test_data.get_internal_test_data_as_string(project, test_name)
        assert data_str == ("data = [\n"
                            "    {\n"
                            "        'key1': 'a',\n"
                            "    },\n"
                            "    {\n"
                            "        'key1': 'b',\n"
                            "    },\n"
                            "]\n")

    def test_get_internal_data_as_string_no_data_var(self, project_class, test_utils):
        _, project = project_class.activate()
        test_name = test_utils.create_random_test(project)
        test_content = ("def test(data):\n"
                        "    pass\n")
        with open(test.Test(project, test_name).path, 'w+') as f:
            f.write(test_content)
        data_str = test_data.get_internal_test_data_as_string(project, test_name)
        assert data_str == ''


class TestGetInternalTestData:

    def test_get_internal_data(self, project_class, test_utils):
        _, project = project_class.activate()
        test_name = test_utils.create_random_test(project)
        test_content = ("data = [\n"
                        "    {'key1': 'a'},\n"
                        "    {'key1': 'b'},\n"
                        "]\n"
                        "def test(data):\n"
                        "    pass\n")
        with open(test.Test(project, test_name).path, 'w+') as f:
            f.write(test_content)
        data = test_data.get_internal_test_data(project, test_name)
        assert data == [{'key1': 'a'}, {'key1': 'b'}]

    def test_get_internal_data_is_dict(self, project_class, test_utils):
        _, project = project_class.activate()
        test_name = test_utils.create_random_test(project)
        test_content = ("data = {'key1': 'a'}\n"
                        "def test(data):\n"
                        "    pass\n")
        with open(test.Test(project, test_name).path, 'w+') as f:
            f.write(test_content)
        data = test_data.get_internal_test_data(project, test_name)
        assert data == [{'key1': 'a'}]

    def test_get_internal_data_not_dict_not_list_of_dicts(self, project_class, test_utils):
        _, project = project_class.activate()
        test_name = test_utils.create_random_test(project)
        test_content = ("data = 'key1'\n"
                        "def test(data):\n"
                        "    pass\n")
        with open(test.Test(project, test_name).path, 'w+') as f:
            f.write(test_content)
        data = test_data.get_internal_test_data(project, test_name)
        assert data == []


class TestGetTestData:

    def test_get_test_data(self, project_class, test_utils):
        _, project = project_class.activate()
        test_name = test_utils.create_random_test(project)
        csv_data = [{'a': ' b'}]
        json_data = '[{"c": "d"}]'
        test_data.save_csv_test_data(project, test_name, csv_data)
        test_data.save_json_test_data(project, test_name, json_data)
        test_content = "data = {'e': 'f'}"
        with open(test.Test(project, test_name).path, 'w+') as f:
            f.write(test_content)
        data = test_data.get_test_data(project, test_name)
        expected = {
            'csv': csv_data,
            'json': json_data,
            'internal': "data = {\n    'e': 'f',\n}"
        }
        assert data == expected


class TestGetParsedTestData:

    def test_get_test_data__csv_and_json(self, project_class, test_utils):
        """Only csv is returned"""
        _, project = project_class.activate()
        test_name = test_utils.create_random_test(project)
        csv_data = [{'a': ' b'}]
        json_data = '[{"c": "d"}]'
        test_data.save_csv_test_data(project, test_name, csv_data)
        test_data.save_json_test_data(project, test_name, json_data)
        data = test_data.get_parsed_test_data(project, test_name)
        assert data == csv_data

    def test_get_test_data__json_and_internal(self, project_class, test_utils):
        """Only json is returned"""
        _, project = project_class.activate()
        test_name = test_utils.create_random_test(project)
        json_data = '[{"c": "d"}]'
        test_data.save_json_test_data(project, test_name, json_data)
        test_content = "data = {'e': 'f'}"
        with open(test.Test(project, test_name).path, 'w+') as f:
            f.write(test_content)
        data = test_data.get_parsed_test_data(project, test_name)
        assert data == json.loads(json_data)
        # remove json data, internal data is now returned
        test_data.remove_json_data_if_present(project, test_name)
        data = test_data.get_parsed_test_data(project, test_name)
        assert data == [{'e': 'f'}]

    def test_get_test_data__no_data(self, project_class, test_utils):
        _, project = project_class.activate()
        test_name = test_utils.create_random_test(project)
        data = test_data.get_parsed_test_data(project, test_name)
        assert data == [{}]
