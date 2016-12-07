from golem.core import utils

from tests.fixtures import project, test_directory


class Test_get_projects:

    def test_get_projects(self, project):
        projects = utils.get_projects(project[0])
        assert project[1] in projects