import os

from golem.core import utils
from golem.gui import page_object

from tests.fixtures import project_fixture, test_directory_fixture


class Test_get_projects:

    def test_get_projects(self, project_fixture):
        projects = utils.get_projects(project_fixture['test_directory_fixture']['full_path'])
        assert project_fixture['project_name'] in projects


class Test_get_files_in_directory_dotted_path:

    def test_get_files_in_directory_dotted_path(self, project_fixture, test_directory_fixture):
        # create a new page object in pages folder
        page_object.new_page_object(test_directory_fixture['full_path'],
                                    project_fixture['project_name'],
                                    [],
                                    'page1')
        # create a new page object in pages/dir/subdir/
        page_object.new_page_object(test_directory_fixture['full_path'],
                                    project_fixture['project_name'],
                                    ['dir', 'subdir'],
                                    'page2')
        base_path = os.path.join(test_directory_fixture['full_path'],
                                 'projects',
                                 project_fixture['project_name'],
                                 'pages')
        dotted_files = utils.get_files_in_directory_dotted_path(base_path)
        assert 'page1' in dotted_files
        assert 'dir.subdir.page2' in dotted_files
        assert len(dotted_files) == 2


