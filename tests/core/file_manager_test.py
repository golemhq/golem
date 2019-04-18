import os

from golem.core import page_object, file_manager


class TestDirectoryElement:

    def test__directory_element(self):
        dir_elem = file_manager._directory_element('elem_type', 'name', 'dot.path')
        expected = {
            'type': 'elem_type',
            'name': 'name',
            'dot_path': 'dot.path',
            'sub_elements': []
        }
        assert dir_elem == expected
        dir_elem = file_manager._directory_element('elem_type', 'name')
        expected = {
            'type': 'elem_type',
            'name': 'name',
            'dot_path': None,
            'sub_elements': []
        }
        assert dir_elem == expected


class TestGenerateFileStructureDict:

    def test_generate_file_structure_dict(self, project_function):
        _, project = project_function.activate()
        page_object.new_page_object(project, [], 'page_one')
        page_object.new_page_object(project, ['module'], 'page_two')
        full_path = page_object.pages_base_dir(project)
        file_structure = file_manager.generate_file_structure_dict(full_path)
        expected_result = {
            'type': 'directory',
            'name': 'pages',
            'dot_path': '.',
            'sub_elements': [
                {
                    'type': 'directory',
                    'name': 'module',
                    'dot_path': 'module',
                    'sub_elements': [
                            {
                                'type': 'file',
                                'name': 'page_two',
                                'dot_path': 'module.page_two',
                                'sub_elements': []
                            }
                        ]
                },
                {
                    'type': 'file',
                    'name': 'page_one',
                    'dot_path': 'page_one',
                    'sub_elements': []
                }
            ]
        }
        assert file_structure == expected_result

    def test_generate_file_structure_dict_empty(self, project_function):
        _, project = project_function.activate()
        full_path = page_object.pages_base_dir(project)
        file_structure = file_manager.generate_file_structure_dict(full_path)
        expected_result = {
            'type': 'directory',
            'name': 'pages',
            'dot_path': '.',
            'sub_elements': [
            ]
        }
        assert file_structure == expected_result


class TestGetFilesDotPath:

    def test_get_files_dot_path(self, project_function):
        _, project = project_function.activate()
        page_object.new_page_object(project, [], 'page1')
        page_object.new_page_object(project, ['dir', 'subdir'], 'page2')
        base_path = os.path.join(project_function.path, 'pages')
        dot_files = file_manager.get_files_dot_path(base_path)
        expected_result = [
            'page1',
            'dir.subdir.page2'
        ]
        assert dot_files == expected_result

    def test_get_files_dot_path_with_extension(self, project_function):
        _, project = project_function.activate()
        page_object.new_page_object(project, [], 'page2')
        base_path = os.path.join(project_function.path, 'pages')
        another_extension = os.path.join(base_path, 'another.json')
        open(another_extension, 'w+').close()
        dot_files = file_manager.get_files_dot_path(base_path, extension='.py')
        expected_result = ['page2']
        assert dot_files == expected_result


class TestCreateDirectory:

    def test_create_directory_path_list(self, dir_function):
        path = dir_function.path
        file_manager.create_directory(path_list=[path, 'a', 'b', 'c'],
                                      add_init=False)
        expected_dir = os.path.join(path, 'a', 'b', 'c')
        assert os.path.isdir(expected_dir)
        init_file_path = os.path.join(expected_dir, '__init__.py')
        assert not os.path.exists(init_file_path)

    def test_create_directory_path(self, dir_function):
        path = dir_function.path
        expected_dir = os.path.join(path, 'd', 'e', 'f')
        file_manager.create_directory(path=expected_dir, add_init=True)
        assert os.path.isdir(expected_dir)
        init_file_path = os.path.join(expected_dir, '__init__.py')
        assert os.path.exists(init_file_path)

    def test_create_directory_with_init(self, dir_function):
        path = dir_function.path
        file_manager.create_directory(path_list=[path, 'a', 'b', 'c'], add_init=True)
        expected_dir = os.path.join(path, 'a', 'b', 'c')
        assert os.path.isdir(expected_dir)
        init_file_path = os.path.join(expected_dir, '__init__.py')
        assert os.path.exists(init_file_path)


class TestRenameFile:

    def test_rename_file(self, dir_function):
        path = dir_function.path
        filename = 'testfile.txt'
        open(filename, 'w+').close()
        new_path = os.path.join(path, 'subfolder')
        new_filename = 'newtestfile.txt'
        error = file_manager.rename_file(path, filename, new_path, new_filename)
        new_full_path = os.path.join(new_path, new_filename)
        assert os.path.isfile(new_full_path)
        assert error == ''

    def test_rename_file_destination_exist(self, dir_function):
        path = dir_function.path
        filename = 'testfile.txt'
        new_filename = 'newtestfile.txt'
        open(filename, 'w').close()
        open(new_filename, 'w+').close()
        error = file_manager.rename_file(path, filename, path, new_filename)
        assert error == 'A file with that name already exists'

    def test_rename_file_source_does_not_exist(self, dir_function):
        path = dir_function.path
        filename = 'testfile.txt'
        new_filename = 'newtestfile.txt'
        error = file_manager.rename_file(path, filename, path, new_filename)
        expected_error = ('File {} does not exist'.format(os.path.join(path, filename)))
        assert error == expected_error


class TestNewDirectoryOfType:

    def test_new_directory_of_type_tests(self, project_class):
        _, project = project_class.activate()
        errors = file_manager.new_directory_of_type(project, [], 'new_test_dir', 'tests')
        expected_dir = os.path.join(project_class.path, 'tests', 'new_test_dir')
        expected_init_path = os.path.join(expected_dir, '__init__.py')
        assert os.path.isdir(expected_dir)
        assert os.path.isfile(expected_init_path)
        assert errors == []

    def test_new_directory_of_type_pages(self, project_class):
        _, project = project_class.activate()
        errors = file_manager.new_directory_of_type(project, [], 'new_pages_dir', 'pages')
        expected_dir = os.path.join(project_class.path, 'pages', 'new_pages_dir')
        expected_init_path = os.path.join(expected_dir, '__init__.py')
        assert os.path.isdir(expected_dir)
        assert os.path.isfile(expected_init_path)
        assert errors == []

    def test_new_directory_of_type_suites(self, project_class):
        _, project = project_class.activate()
        errors = file_manager.new_directory_of_type(project, [], 'new_suites_dir', 'suites')
        expected_dir = os.path.join(project_class.path, 'suites', 'new_suites_dir')
        expected_init_path = os.path.join(expected_dir, '__init__.py')
        assert os.path.isdir(expected_dir)
        assert os.path.isfile(expected_init_path)
        assert errors == []

    def test_new_directory_of_type_invalid_type(self, project_class):
        _, project = project_class.activate()
        errors = file_manager.new_directory_of_type(project, [], 'new_suites_dir', 'invalid_type')
        assert errors == ['invalid_type is not a valid dir_type']

    def test_new_directory_of_type_already_exist(self, project_class):
        _, project = project_class.activate()
        file_manager.new_directory_of_type(project, [], 'new_suites_dir_two', 'suites')
        errors = file_manager.new_directory_of_type(project, [], 'new_suites_dir_two', 'suites')
        assert errors == ['A directory with that name already exists']
