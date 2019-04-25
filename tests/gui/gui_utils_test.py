import os
import pytest

from golem.gui import gui_utils
from golem.core import errors


DOCSTRINGS = [
    {
        'actual': """some description

        Parameters:
        param1 : value
        """,
        'expected': {
            'description': 'some description',
            'parameters': [{'name': 'param1', 'type': 'value'}]
        }
    },
    {
        'actual': """some description with
        multiline

        Parameters:
        param1 : value
        """,
        'expected': {
            'description': 'some description with multiline',
            'parameters': [{'name': 'param1', 'type': 'value'}]
        }
    },
    {
        'actual': """some description with
        
        blank lines

        Parameters:
        param1 : value
        """,
        'expected': {
            'description': 'some description with blank lines',
            'parameters': [{'name': 'param1', 'type': 'value'}]
        }
    },
    {
        'actual': """multiple parameters

        Parameters:
        param1 : value
        param2 (with desc and spaces etc) : element
        param3 : value
        param4 : element
        """,
        'expected': {
            'description': 'multiple parameters',
            'parameters': [{'name': 'param1', 'type': 'value'},
                           {'name': 'param2 (with desc and spaces etc)', 'type': 'element'},
                           {'name': 'param3', 'type': 'value'},
                           {'name': 'param4', 'type': 'element'}]
        }
    },
    {
        'actual': """
        Parameters:
        no description : value
        """,
        'expected': {
            'description': '',
            'parameters': [{'name': 'no description', 'type': 'value'}]
        }
    },
    {
        'actual': """no parameters
        
        """,
        'expected': {
            'description': 'no parameters',
            'parameters': []
        }
    }
]


class TestGolemActionParser:

    @pytest.mark.parametrize('actual,expected',
                             [(x['actual'], x['expected']) for x in DOCSTRINGS])
    def test__parse_docstring(self, actual, expected):
        expected = gui_utils.Golem_action_parser()._parse_docstring(actual)
        assert expected == expected


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

