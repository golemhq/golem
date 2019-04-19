"""Main point of entrance to the application"""
import sys

from .core import session, utils
from .core.settings_manager import get_global_settings
from .cli import argument_parser, commands


def execute_from_command_line(testdir):
    # deactivate .pyc extention file generation
    sys.dont_write_bytecode = True
    sys.path.insert(0, '')

    if not utils.is_valid_test_directory(testdir):
        sys.exit('Error: current drectory is not an existing Golem test '
                 'directory; .golem file not found')

    # set global values
    session.testdir = testdir
    session.settings = get_global_settings()

    parser = argument_parser.get_parser()
    args = parser.parse_args()
    commands.command_dispatcher(args)
