import os

from golem.core import page, file_manager
from golem.core.project import Project


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
        page.create_page(project, 'page_one')
        page.create_page(project, 'module.page_two')
        path = Project(project).page_directory_path
        file_structure = file_manager.generate_file_structure_dict(path)
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
        path = Project(project).page_directory_path
        file_structure = file_manager.generate_file_structure_dict(path)
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
        page.create_page(project, 'page1')
        page.create_page(project, 'dir.subdir.page2')
        base_path = os.path.join(project_function.path, 'pages')
        dot_files = file_manager.get_files_dot_path(base_path)
        expected_result = [
            'page1',
            'dir.subdir.page2'
        ]
        assert dot_files == expected_result

    def test_get_files_dot_path_with_extension(self, project_function):
        _, project = project_function.activate()
        page.create_page(project, 'page2')
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


class TestCreatePackage:

    def test_create_package(self, dir_function):
        path = dir_function.path
        expected_dir = os.path.join(path, 'd', 'e', 'f')
        file_manager.create_package(path=expected_dir)
        assert os.path.isdir(expected_dir)
        init_file_path = os.path.join(expected_dir, '__init__.py')
        assert os.path.exists(init_file_path)


class TestRenameFile:

    def test_rename_file(self, dir_function):
        path = dir_function.path
        oldpath = os.path.join(path, 'testfile.txt')
        open(oldpath, 'w+').close()
        newpath = os.path.join(path, 'subfolder', 'newtestfile.txt')
        errors = file_manager.rename_file(oldpath, newpath)
        assert errors == []
        assert not os.path.isfile(oldpath)
        assert os.path.isfile(newpath)

    def test_rename_file_destination_exist(self, dir_function):
        path = dir_function.path
        oldpath = os.path.join(path, 'testfile.txt')
        open(oldpath, 'w+').close()
        newpath = os.path.join(path, 'newtestfile.txt')
        open(newpath, 'w+').close()
        errors = file_manager.rename_file(oldpath, newpath)
        assert os.path.isfile(oldpath)
        assert os.path.isfile(newpath)
        assert errors == ['A file with that name already exists']

    def test_rename_file_source_does_not_exist(self, dir_function):
        path = dir_function.path
        oldpath = os.path.join(path, 'testfile.txt')
        newpath = os.path.join(path, 'subfolder', 'newtestfile.txt')
        errors = file_manager.rename_file(oldpath, newpath)
        expected_error = ('File {} does not exist'.format(oldpath))
        assert errors == [expected_error]
        assert not os.path.isfile((newpath))


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


class TestCreatePackageDirectories:

    def test_create_package_directories(self, dir_function):
        basepath = dir_function.path
        # one folder level
        relpath = os.path.join('a')
        file_manager.create_package_directories(basepath, relpath)
        assert os.path.isdir(os.path.join(basepath, 'a'))
        assert os.path.isfile(os.path.join(basepath, 'a', '__init__.py'))
        # two folder levels
        relpath = os.path.join('b', 'c')
        file_manager.create_package_directories(basepath, relpath)
        assert os.path.isdir(os.path.join(basepath, 'b', 'c'))
        assert os.path.isfile(os.path.join(basepath, 'b', '__init__.py'))
        assert os.path.isfile(os.path.join(basepath, 'b', 'c', '__init__.py'))
        # folder only, no file in path
        relpath = os.path.join('d', 'e', 'f') + os.sep
        file_manager.create_package_directories(basepath, relpath)
        assert os.path.isdir(os.path.join(basepath, 'd', 'e', 'f'))
        assert os.path.isfile(os.path.join(basepath, 'd', 'e', 'f', '__init__.py'))

