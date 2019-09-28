import os

import pytest

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
            'dot_path': '',
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
            'dot_path': '',
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


class TestRenameDirectory:

    def test_rename_directory(self, dir_function):
        basepath = dir_function.path
        src = 'a'
        dst = 'b'
        file_manager.create_package_directories(basepath, src)
        errors = file_manager.rename_directory(basepath, src, dst)
        assert errors == []
        assert not os.path.isdir(os.path.join(basepath, src))
        assert os.path.isdir(os.path.join(basepath, dst))
        assert os.path.isfile(os.path.join(basepath, dst, '__init__.py'))

        src = 'q'
        dst = os.sep.join(['w', 'e'])
        file_manager.create_package_directories(basepath, src)
        errors = file_manager.rename_directory(basepath, src, dst)
        assert errors == []
        assert not os.path.isdir(os.path.join(basepath, src))
        assert os.path.isdir(os.path.join(basepath, dst))
        assert os.path.isfile(os.path.join(basepath, dst, '__init__.py'))

    def test_rename_directory_with_files_and_folders(self, dir_function, test_utils):
        basepath = dir_function.path
        src = 'a'
        dst = 'b'
        subfolder = 'c'
        file_manager.create_package_directories(basepath, src)
        test_utils.create_empty_file(os.path.join(basepath, src), 'foo.txt')
        test_utils.create_empty_file(os.path.join(basepath, src, subfolder), 'bar.txt')
        errors = file_manager.rename_directory(basepath, src, dst)
        assert errors == []
        assert not os.path.isdir(os.path.join(basepath, src))
        assert os.path.isdir(os.path.join(basepath, dst))
        assert os.path.isdir(os.path.join(basepath, dst, subfolder))
        assert os.path.isfile(os.path.join(basepath, dst, '__init__.py'))
        assert os.path.isfile(os.path.join(basepath, dst, 'foo.txt'))
        assert os.path.isfile(os.path.join(basepath, dst, subfolder, 'bar.txt'))

    def test_rename_directory_src_does_not_exist(self, dir_function):
        basepath = dir_function.path
        src = 'a'
        dst = 'b'
        errors = file_manager.rename_directory(basepath, src, dst)
        assert errors == ['Directory {} does not exist'.format(src)]
        assert not os.path.isdir(os.path.join(basepath, dst))

    def test_rename_directory_src_is_not_a_directory(self, dir_function, test_utils):
        basepath = dir_function.path
        src = 'a'
        dst = 'b'
        test_utils.create_empty_file(basepath, src)
        errors = file_manager.rename_directory(basepath, src, dst)
        assert errors == ['Path {} is not a directory'.format(src)]
        assert not os.path.isdir(os.path.join(basepath, dst))

    def test_rename_directory_dst_exists(self, dir_function, test_utils):
        """It should return an error when dst is an existing file or folder"""
        basepath = dir_function.path
        # dst is file
        src = 'a'
        dst = 'b'
        file_manager.create_package_directories(basepath, src)
        test_utils.create_empty_file(basepath, dst)
        errors = file_manager.rename_directory(basepath, src, dst)
        assert errors == ['Path {} already exists'.format(dst)]
        assert os.path.isdir(os.path.join(basepath, src))
        assert os.path.isfile(os.path.join(basepath, dst))
        # dst is directory
        src = 'c'
        dst = 'd'
        file_manager.create_package_directories(basepath, src)
        file_manager.create_package_directories(basepath, dst)
        errors = file_manager.rename_directory(basepath, src, dst)
        assert errors == ['Path {} already exists'.format(dst)]
        assert os.path.isdir(os.path.join(basepath, src))
        assert os.path.isdir(os.path.join(basepath, dst))

    def test_rename_directory_to_child_path(self, dir_function, test_utils):
        """file_manager.rename_directory should return 'Error: PermissionError'
        When renaming a directory to a descendant path.
        """
        basepath = dir_function.path
        src = 'a'
        dst = os.sep.join([src, 'b'])
        file_manager.create_package_directories(basepath, src)
        test_utils.create_empty_file(os.path.join(basepath, src), 'foo.txt')
        errors = file_manager.rename_directory(basepath, src, dst)
        if os.name == 'nt':
            assert errors == ['Error: PermissionError']
        else:
            assert errors == ['An error occurred while renaming folder']
        assert os.path.isdir(os.path.join(basepath, src))
        assert not os.path.isdir(os.path.join(basepath, dst))
        assert os.path.isfile(os.path.join(basepath, src, '__init__.py'))
        assert os.path.isfile(os.path.join(basepath, src, 'foo.txt'))

    def test_rename_directory_to_parent_path(self, dir_function, test_utils):
        """file_manager.rename_directory should return an error
        When renaming a directory to a parent path.
        """
        basepath = dir_function.path
        dst = 'a'
        src = os.sep.join([dst, 'b'])
        file_manager.create_package_directories(basepath, src)
        test_utils.create_empty_file(os.path.join(basepath, src), 'foo.txt')
        errors = file_manager.rename_directory(basepath, src, dst)
        assert errors == ['Path {} already exists'.format(dst)]
        assert os.path.isdir(os.path.join(basepath, src))
        assert os.path.isdir(os.path.join(basepath, dst))
        assert os.path.isfile(os.path.join(basepath, src, '__init__.py'))
        assert os.path.isfile(os.path.join(basepath, src, 'foo.txt'))

    @pytest.mark.skipif("os.name != 'nt'")
    def test_rename_directory_a_file_is_open(self, dir_function, test_utils):
        """A directory cannot be renamed if a child file is currently
        opened by another process.
        """
        basepath = dir_function.path
        src = 'a'
        dst = 'b'
        file_manager.create_package_directories(basepath, src)
        filepath = test_utils.create_empty_file(os.path.join(basepath, src), 'foo.txt')
        filepath_two = test_utils.create_empty_file(os.path.join(basepath, src), 'bar.txt')
        with open(filepath):
            errors = file_manager.rename_directory(basepath, src, dst)
            assert errors == ['Error: PermissionError']
        assert not os.path.isdir(os.path.join(basepath, dst))
        assert os.path.isdir(os.path.join(basepath, src))
        assert os.path.isfile(filepath)
        assert os.path.isfile(filepath_two)


class TestDeleteDirectory:

    def test_delete_directory(self, dir_function):
        basepath = dir_function.path
        directory = 'a'
        file_manager.create_package_directories(basepath, directory)
        path = os.path.join(basepath, directory)
        errors = file_manager.delete_directory(path)
        assert errors == []
        assert not os.path.isdir(path)

    def test_delete_directory_does_not_exist(self, dir_function):
        basepath = dir_function.path
        directory = 'a'
        path = os.path.join(basepath, directory)
        errors = file_manager.delete_directory(path)
        assert errors == ['Directory does not exist']

    def test_delete_directory_with_files_and_folders(self, dir_function, test_utils):
        basepath = dir_function.path
        directory = 'a'
        file_manager.create_package_directories(basepath, directory)
        file_manager.create_package_directories(os.path.join(basepath, directory), 'foo')
        test_utils.create_empty_file(os.path.join(basepath, directory), 'bar.txt')
        path = os.path.join(basepath, directory)
        errors = file_manager.delete_directory(path)
        assert errors == []
        assert not os.path.isdir(path)

    @pytest.mark.skipif("os.name != 'nt'")
    def test_delete_directory_a_child_file_is_open(self, dir_function, test_utils):
        basepath = dir_function.path
        directory = 'a'
        file_manager.create_package_directories(basepath, directory)
        filename_one = test_utils.create_empty_file(os.path.join(basepath, directory), 'foo.txt')
        filename_two = test_utils.create_empty_file(os.path.join(basepath, directory), 'bar.txt')
        path = os.path.join(basepath, directory)
        with open(filename_one):
            errors = file_manager.delete_directory(path)
            assert errors == ['Error: PermissionError']
        assert os.path.isdir(path)
        # open file was not removed
        assert os.path.isfile(filename_one)
        # not open file was removed
        assert not os.path.isfile(filename_two)


class TestPathIsParentOfPath:

    def test_path_is_parent_of_path(self):
        path = os.path.abspath(os.path.join('a', 'b'))
        spath = os.path.abspath('a')
        assert not file_manager.path_is_parent_of_path(path, spath)
        assert file_manager.path_is_parent_of_path(spath, path)

        path = os.path.abspath(os.path.join('foo', 'bar'))
        spath = os.path.abspath('foobar')
        assert not file_manager.path_is_parent_of_path(path, spath)
        assert not file_manager.path_is_parent_of_path(spath, path)

        path = os.path.abspath(os.path.join('foo', 'bar', 'baz'))
        spath = os.path.abspath(os.path.join('foo', 'blah', 'baz'))
        assert not file_manager.path_is_parent_of_path(path, spath)
        assert not file_manager.path_is_parent_of_path(spath, path)