import os
import pytest

from golem.gui import gui_utils
from golem.core import errors, settings_manager, project


DOCSTRINGS = [
    (
        """some description

        Parameters:
        param1 : value
        """,
        ('some description', [{'name': 'param1', 'type': 'value'}])
    ),
    (
        """some description with
        multiline

        Parameters:
        param1 : value
        """,
        ('some description with multiline', [{'name': 'param1', 'type': 'value'}])
    ),
    (
        """some description with
        
        blank lines

        Parameters:
        param1 : value
        """,
        ('some description with blank lines', [{'name': 'param1', 'type': 'value'}])
    ),
    (
        """multiple parameters

        Parameters:
        param1 : value
        param2 (with desc and spaces etc) : element
        param3 : value
        param4 : element
        """,
        ('multiple parameters',
         [{'name': 'param1', 'type': 'value'},
          {'name': 'param2 (with desc and spaces etc)', 'type': 'element'},
          {'name': 'param3', 'type': 'value'},
          {'name': 'param4', 'type': 'element'}])
    ),
    (
        """
        Parameters:
        no description : value
        """,
        ('', [{'name': 'no description', 'type': 'value'}])
    ),
    (
        """no parameters
        
        """,
        ('no parameters', [])
    )
]


class TestGolemActionParser:

    @pytest.mark.parametrize('docstring, expected', DOCSTRINGS)
    def test__parse_docstring(self, docstring, expected):
        description, parameters = gui_utils.GolemActionParser()._parse_docstring(docstring)
        assert description == expected[0]
        assert parameters == expected[1]

    def test_get_actions(self, project_function):
        _, project = project_function.activate()
        # no project, default global setting is true
        actions = gui_utils.GolemActionParser().get_actions()
        assert any(action['name'] == 'click' for action in actions)
        # implicit_actions_import = false - project level
        settings_manager.save_project_settings(project, '{"implicit_actions_import": false}')
        actions = gui_utils.GolemActionParser().get_actions(project)
        assert any(action['name'] == 'actions.click' for action in actions)
        # implicit_actions_import = true - project level
        settings_manager.save_project_settings(project, '{"implicit_actions_import": true}')
        actions = gui_utils.GolemActionParser().get_actions()
        assert any(action['name'] == 'click' for action in actions)


class TestGetSecretKey:

    def test_get_secret_key(self, testdir_function):
        testdir_function.activate()
        secret_key = gui_utils.get_secret_key()
        assert type(secret_key) == str

    def test_get_secret_key_golem_file_missing(self, testdir_function):
        testdir = testdir_function.activate()
        golem_file_path = os.path.join(testdir, '.golem')
        os.remove(golem_file_path)
        with pytest.raises(SystemExit) as wrapped_execution:
            gui_utils.get_secret_key()
        expected = errors.invalid_test_directory.format(testdir)
        assert wrapped_execution.value.code == expected

    def test_get_secret_key_golem_file_missing_gui_key_section(self, testdir_function, capsys):
        testdir = testdir_function.activate()
        golem_file_path = os.path.join(testdir, '.golem')
        with open(golem_file_path, 'w') as f:
            f.write('')
        secret_key = gui_utils.get_secret_key()
        out, _ = capsys.readouterr()
        assert 'Warning: gui config section not found in .golem file. Using default secret key' in out
        assert secret_key == gui_utils.DEFAULT_SECRET_KEY

    def test_get_secret_key_golem_file_missing_secret_key(self, testdir_function, capsys):
        testdir = testdir_function.activate()
        golem_file_path = os.path.join(testdir, '.golem')
        with open(golem_file_path, 'w') as f:
            f.write('[gui]\n')
        secret_key = gui_utils.get_secret_key()
        out, _ = capsys.readouterr()
        assert 'Warning: secret_key not found in .golem file. Using default secret key' in out
        assert secret_key == gui_utils.DEFAULT_SECRET_KEY


class TestProjectsCache:

    def test_projects_cache(self, testdir_function, test_utils):
        _ = testdir_function.activate()
        gui_utils.ProjectsCache._projects = None
        assert gui_utils.ProjectsCache.get() == []
        project_name = test_utils.random_string()
        project.create_project(project_name)
        gui_utils.ProjectsCache._projects = None
        assert gui_utils.ProjectsCache.get() == [project_name]
        project_name_two = test_utils.random_string()
        gui_utils.ProjectsCache.add(project_name_two)
        assert gui_utils.ProjectsCache.get() == [project_name, project_name_two]
        gui_utils.ProjectsCache.remove(project_name_two)
        assert gui_utils.ProjectsCache.get() == [project_name]
