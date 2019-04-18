import os

from golem.core import test_data


class TestSaveExternalTestDataFile:

    def test_save_external_data(self, project_function_clean, test_utils):
        _, project = project_function_clean.activate()
        test_name = test_utils.random_string(10, 'test')
        input_test_data = [{'key1': 'value1', 'key2': 'value2'},
                           {'key1': 'value3', 'key2': 'value4'}]
        test_data.save_external_test_data_file(project, test_name, input_test_data)
        data_path = os.path.join(project_function_clean.path, 'tests', test_name+'.csv')
        with open(data_path) as f:
            result = f.read()
            expected = ('key1,key2\nvalue1,value2\nvalue3,value4\n')
            expected_var = ('key2,key1\nvalue2,value1\nvalue4,value3\n')
            assert result == expected or result == expected_var

    def test_save_external_data_empty_data(self, project_function_clean, test_utils):
        _, project = project_function_clean.activate()
        test_name = test_utils.random_string(10, 'test')
        input_test_data = []
        test_data.save_external_test_data_file(project, test_name, input_test_data)
        data_path = os.path.join(project_function_clean.path, 'tests', test_name+'.csv')
        assert not os.path.isfile(data_path)

    def test_save_external_data_empty_data_file_exists(self, project_function_clean, test_utils):
        _, project = project_function_clean.activate()
        test_name = test_utils.random_string(10, 'test')
        input_test_data = []
        data_path = os.path.join(project_function_clean.path, 'tests', test_name+'.csv')
        open(data_path, 'w+').close()
        test_data.save_external_test_data_file(project, test_name, input_test_data)
        with open(data_path) as f:
            assert f.read() == ''

    def test_save_external_data_special_cases(self, project_function_clean, test_utils):
        _, project = project_function_clean.activate()
        test_name = test_utils.random_string(10, 'test')
        input_test_data = [{'key1': 'string with spaces'},
                           {'key1': 'string "with" quotes'},
                           {'key1': 'string \'with\' quotes'},
                           {'key1': '"quoted_string"'},
                           {'key1': '\'quoted_string\''}]
        test_data.save_external_test_data_file(project, test_name, input_test_data)
        data_path = os.path.join(project_function_clean.path, 'tests', test_name+'.csv')
        with open(data_path) as f:
            result = f.read()
            expected = ('key1\n'
                        'string with spaces\n'
                        '"string ""with"" quotes"\n'
                        'string \'with\' quotes\n'
                        '"""quoted_string"""\n'
                        '\'quoted_string\'\n')
            assert result == expected


class TestGetExternalTestData:

    def test_get_external_test_data(self, project_function_clean, test_utils):
        _, project = project_function_clean.activate()
        test_name = test_utils.random_string(10, 'test')
        data_path = os.path.join(project_function_clean.path, 'tests', test_name + '.csv')
        input = ('key1,key2\nvalue1,value2\nvalue3,value4\n')
        with open(data_path, 'w+') as f:
            f.write(input)
        result = test_data.get_external_test_data(project, test_name)
        expected = [{'key1': 'value1', 'key2': 'value2'},
                    {'key1': 'value3', 'key2': 'value4'}]
        assert result == expected

    def test_get_external_test_data_file_not_exists(self, project_function_clean, test_utils):
        _, project = project_function_clean.activate()
        test_name = test_utils.random_string(10, 'test')
        result = test_data.get_external_test_data(project, test_name)
        assert result == []

    def test_get_external_test_data_special_cases(self, project_function_clean, test_utils):
        _, project = project_function_clean.activate()
        test_name = test_utils.random_string(10, 'test')
        data_path = os.path.join(project_function_clean.path, 'tests', test_name + '.csv')
        input = ('key1\n'
                 'string with spaces\n'
                 '"string ""with"" quotes"\n'
                 'string \'with\' quotes\n'
                 '"""quoted_string"""\n'
                 '\'quoted_string\'\n')
        with open(data_path, 'w+') as f:
            f.write(input)
        result = test_data.get_external_test_data(project, test_name)
        expected = [{'key1': 'string with spaces'},
                    {'key1': 'string "with" quotes'},
                    {'key1': 'string \'with\' quotes'},
                    {'key1': '"quoted_string"'},
                    {'key1': '\'quoted_string\''}]
        assert result == expected


class TestGetInternalTestData:

    def test_get_internal_test_data_list(self, project_function_clean):
        _, project = project_function_clean.activate()
        test_name = 'test_get_internal_test_data'
        test_content = ("data = [\n"
                        "    {\n"
                        "        'key1': 'value1',\n"
                        "        'key2': 'value2',\n"
                        "    },\n"
                        "    {\n"
                        "        'key1': 'value3',\n"
                        "        'key2': 'value4',\n"
                        "    },\n"
                        "]\n")
        test_path = os.path.join(project_function_clean.path, 'tests', test_name+'.py')
        with open(test_path, 'w+') as f:
            f.write(test_content)
        expected = [
            {'key1': 'value1', 'key2': 'value2'},
            {'key1': 'value3', 'key2': 'value4'}
        ]
        internal_data = test_data.get_internal_test_data(project, test_name)
        assert internal_data == expected

    def test_get_internal_test_data_dict(self, project_function_clean):
        _, project = project_function_clean.activate()
        test_name = 'test_get_internal_test_data'
        test_content = ("data = {\n"
                        "    'key1': 'value1',\n"
                        "    'key2': 'value2',\n"
                        "}\n")
        test_path = os.path.join(project_function_clean.path, 'tests', test_name+'.py')
        with open(test_path, 'w+') as f:
            f.write(test_content)
        expected = [{'key1': 'value1', 'key2': 'value2'}]
        internal_data = test_data.get_internal_test_data(project, test_name)
        assert internal_data == expected

    def test_get_internal_test_data_special_cases(self, project_function_clean):
        _, project = project_function_clean.activate()
        test_name = 'test_get_internal_test_data'
        test_content = ("data = [\n"
                        "    {\n"
                        "        'key1': 12,\n"
                        "        'key2': 1.2,\n"
                        "        'key3': False,\n"
                        "        'key4': None,\n"
                        "        'key5': [1,2,3],\n"
                        "        'key6': ['a','b'],\n"
                        "        'key7': {'key1': 'a', \"key2\": \"b\"},\n"
                        "        'key8': (1, '2'),\n"
                        "        'key9': 'test',\n"
                        "        'key10': \"test\",\n"
                        "        'key11': 'te\"s\"t',\n"
                        "        'key12': \"te's't\",\n"
                        "    }\n"
                        "]\n")
        test_path = os.path.join(project_function_clean.path, 'tests', test_name+'.py')
        with open(test_path, 'w+') as f:
            f.write(test_content)
        expected = [
            {'key1': 12,
             'key2': 1.2,
             'key3': False,
             'key4': None,
             'key5': [1,2,3],
             'key6': ['a', 'b'],
             'key7': {'key1': 'a', 'key2': 'b'},
             'key8': (1, '2'),
             'key9': 'test',
             'key10': 'test',
             'key11': 'te"s"t',
             'key12': "te's't"}
        ]
        internal_data = test_data.get_internal_test_data(project, test_name)
        assert internal_data == expected

    def test_get_internal_test_data_repr(self, project_function_clean):
        _, project = project_function_clean.activate()
        test_name = 'test_get_internal_test_data'
        test_content = ("data = [\n"
                        "    {\n"
                        "        'key1': 12,\n"
                        "        'key2': 1.2,\n"
                        "        'key3': False,\n"
                        "        'key4': None,\n"
                        "        'key5': [1,2,3],\n"
                        "        'key6': ['a','b'],\n"
                        "        'key7': {'key1': 'a', \"key2\": \"b\"},\n"
                        "        'key8': (1, '2'),\n"
                        "        'key9': 'test',\n"
                        "        'key10': \"test\",\n"
                        "        'key11': 'te\"s\"t',\n"
                        "        'key12': \"te's't\",\n"
                        "    }\n"
                        "]\n")
        test_path = os.path.join(project_function_clean.path, 'tests', test_name+'.py')
        with open(test_path, 'w+') as f:
            f.write(test_content)
        expected = [
            {'key1': 12,
             'key2': 1.2,
             'key3': False,
             'key4': None,
             'key5': [1,2,3],
             'key6': ['a', 'b'],
             'key7': {'key1': 'a', 'key2': 'b'},
             'key8': (1, '2'),
             'key9': "'test'",
             'key10': "'test'",
             'key11': '\'te"s"t\'',
             'key12': '"te\'s\'t"'}
        ]
        internal_data = test_data.get_internal_test_data(project, test_name, repr_strings=True)
        assert internal_data == expected

    def test_get_internal_test_data_no_data_var(self, project_function_clean):
        _, project = project_function_clean.activate()
        test_name = 'test_get_internal_test_data_no_data_var'
        test_content = "there_is = 'no data here'\n"
        test_path = os.path.join(project_function_clean.path, 'tests', test_name+'.py')
        with open(test_path, 'w+') as f:
            f.write(test_content)
        internal_data = test_data.get_internal_test_data(project, test_name)
        assert internal_data == []

    def test_get_internal_test_data_not_dict_not_list(self, project_function_clean, capsys):
        _, project = project_function_clean.activate()
        test_name = 'test_get_internal_test_data'
        test_content = "data = 'just a string'\n"
        test_path = os.path.join(project_function_clean.path, 'tests', test_name+'.py')
        with open(test_path, 'w+') as f:
            f.write(test_content)
        internal_data = test_data.get_internal_test_data(project, test_name)
        assert internal_data == []
        captured = capsys.readouterr()
        msg = 'Warning: infile test data must be a dictionary or a list of dictionaries'
        assert msg in captured.out


class TestGetTestData:

    def test_get_test_data_from_infile(self, project_class, test_utils):
        _, project = project_class.activate()
        test_name = test_utils.random_string(5, 'test')
        test_content = ("data = {\n"
                        "    'key1': 'value1',\n"
                        "    'key2': 'value2',\n"
                        "}\n")
        test_path = os.path.join(project_class.path, 'tests', test_name + '.py')
        with open(test_path, 'w+') as f:
            f.write(test_content)
        expected = [{'key1': 'value1', 'key2': 'value2'}]
        returned_data = test_data.get_test_data(project, test_name)
        assert returned_data == expected

    def test_get_test_data_from_csv(self, project_class, test_utils):
        """when there is csv and infile data, csv has priority"""
        _, project = project_class.activate()
        test_name = test_utils.random_string(5, 'test')
        test_content = ("data = {\n"
                        "    'key1': 'value1',\n"
                        "    'key2': 'value2',\n"
                        "}\n")
        test_path = os.path.join(project_class.path, 'tests', test_name + '.py')
        with open(test_path, 'w+') as f:
            f.write(test_content)
        data_path = os.path.join(project_class.path, 'tests', test_name + '.csv')
        with open(data_path, 'w+') as f:
            f.write('key1,key2\nvalue3,value4\n')
        returned_data = test_data.get_test_data(project, test_name)
        expected = [{'key1': 'value3', 'key2': 'value4'}]
        assert returned_data == expected

    def test_get_test_data_no_data(self, project_class, test_utils):
        """when there is csv and infile data, csv has priority"""
        _, project = project_class.activate()
        test_name = test_utils.random_string(5, 'test')
        test_content = "there_is = 'no data'\n"
        test_path = os.path.join(project_class.path, 'tests', test_name + '.py')
        with open(test_path, 'w+') as f:
            f.write(test_content)
        returned_data = test_data.get_test_data(project, test_name)
        assert returned_data == [{}]
