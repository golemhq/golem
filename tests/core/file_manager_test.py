
import os

from golem.core import page_object, file_manager, utils

from tests import helper_functions
from tests.fixtures import testdir_fixture


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
        assert 'page1' in dotted_files
        assert 'dir.subdir.page2' in dotted_files
        assert len(dotted_files) == 2
