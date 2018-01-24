
import os

from golem.core import page_object, file_manager, utils

from tests import helper_functions
from tests.fixtures import testdir_fixture, random_project_fixture


class Test___directory_element:

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


class Test_generate_file_structure_dict:

    def test_generate_file_structure_dict(self, random_project_fixture):
        project = random_project_fixture['name']
        testdir = random_project_fixture['testdir']
        page_object.new_page_object(testdir, project, [], 'page_one')
        page_object.new_page_object(testdir, project, ['module'], 'page_two',
                                    add_parents=True)
        full_path = page_object.pages_base_dir(testdir, project)
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


class Test_get_files_dot_path:

    def test_get_files_dot_path(self, testdir_fixture):
        project = helper_functions.create_random_project(testdir_fixture['path'])
        # create a new page object in pages folder
        page_object.new_page_object(testdir_fixture['path'],
                                    project,
                                    [],
                                    'page1')
        # create a new page object in pages/dir/subdir/
        page_object.new_page_object(testdir_fixture['path'],
                                    project,
                                    ['dir', 'subdir'],
                                    'page2',
                                    add_parents=True)
        base_path = os.path.join(testdir_fixture['path'],
                                 'projects',
                                 project,
                                 'pages')
        dotted_files = file_manager.get_files_dot_path(base_path)
        expected_result = [
            'page1',
            'dir.subdir.page2'
        ]
        assert dotted_files == expected_result


class Test_create_directory:

    def test_create_directory_path_list(self, random_project_fixture):
        project = random_project_fixture['name']
        testdir = random_project_fixture['testdir']
        base_dir = page_object.pages_base_dir(testdir, project)
        file_manager.create_directory(path_list=[base_dir, 'a', 'b', 'c'],
                                      add_init=False)
        expected_dir = os.path.join(base_dir, 'a', 'b', 'c')
        assert os.path.isdir(expected_dir)
        init_file_path = os.path.join(expected_dir, '__init__.py')
        assert not os.path.exists(init_file_path)


    def test_create_directory_path(self, random_project_fixture):
        project = random_project_fixture['name']
        testdir = random_project_fixture['testdir']
        base_dir = page_object.pages_base_dir(testdir, project)
        expected_dir = os.path.join(base_dir, 'd', 'e', 'f')
        file_manager.create_directory(path=expected_dir,
                                      add_init=True)
        assert os.path.isdir(expected_dir)
        init_file_path = os.path.join(expected_dir, '__init__.py')
        assert os.path.exists(init_file_path)


class Test_rename_file:

    def test_rename_file(self, random_project_fixture):
        project = random_project_fixture['name']
        testdir = random_project_fixture['testdir']
        page_object.new_page_object(testdir, project, [], 'page_one')
        base_dir = page_object.pages_base_dir(testdir, project)
        new_path = os.path.join(base_dir, 'submodule')
        error = file_manager.rename_file(base_dir, 'page_one.py',
                                        new_path, 'page_one_edit.py')
        new_full_path = os.path.join(new_path, 'page_one_edit.py')
        assert os.path.isfile(new_full_path)
        assert error == ''


    def test_rename_file_destination_exist(self, random_project_fixture):
        project = random_project_fixture['name']
        testdir = random_project_fixture['testdir']
        page_object.new_page_object(testdir, project, [], 'page_two')
        page_object.new_page_object(testdir, project, [], 'destination')
        base_dir = page_object.pages_base_dir(testdir, project)
        error = file_manager.rename_file(base_dir, 'page_one.py',
                                         base_dir, 'destination.py')
        expected_error = ('File {} already exists'
                          .format(os.path.join(base_dir, 'destination.py')))
        assert error == expected_error


class Test_new_directory_of_type:

    def test_new_directory_of_type_tests(self, random_project_fixture):
        project = random_project_fixture['name']
        testdir = random_project_fixture['testdir']
        errors = file_manager.new_directory_of_type(testdir, project, [],
                                                    'new_test_dir', 'tests')
        expected_dir = os.path.join(testdir, 'projects', project, 'tests',
                                    'new_test_dir')
        expected_init_path = os.path.join(expected_dir, '__init__.py')
        assert os.path.isdir(expected_dir)
        assert os.path.isfile(expected_init_path)
        assert errors == []


    def test_new_directory_of_type_pages(self, random_project_fixture):
        project = random_project_fixture['name']
        testdir = random_project_fixture['testdir']
        errors = file_manager.new_directory_of_type(testdir, project, [],
                                                    'new_pages_dir', 'pages')
        expected_dir = os.path.join(testdir, 'projects', project, 'pages',
                                    'new_pages_dir')
        expected_init_path = os.path.join(expected_dir, '__init__.py')
        assert os.path.isdir(expected_dir)
        assert os.path.isfile(expected_init_path)
        assert errors == []


    def test_new_directory_of_type_suites(self, random_project_fixture):
        project = random_project_fixture['name']
        testdir = random_project_fixture['testdir']
        errors = file_manager.new_directory_of_type(testdir, project, [],
                                                    'new_suites_dir', 'suites')
        expected_dir = os.path.join(testdir, 'projects', project, 'suites',
                                    'new_suites_dir')
        expected_init_path = os.path.join(expected_dir, '__init__.py')
        assert os.path.isdir(expected_dir)
        assert os.path.isfile(expected_init_path)
        assert errors == []


    def test_new_directory_of_type_invalid_type(self, random_project_fixture):
        project = random_project_fixture['name']
        testdir = random_project_fixture['testdir']
        errors = file_manager.new_directory_of_type(testdir, project, [],
                                                    'new_suites_dir', 'invalid_type')
        assert errors == ['invalid_type is not a valid dir_type']


    def test_new_directory_of_type_already_exist(self, random_project_fixture):
        project = random_project_fixture['name']
        testdir = random_project_fixture['testdir']
        file_manager.new_directory_of_type(testdir, project, [],
                                                    'new_suites_dir_two', 'suites')
        errors = file_manager.new_directory_of_type(testdir, project, [],
                                                    'new_suites_dir_two', 'suites')
        assert errors == ['A directory with that name already exists']