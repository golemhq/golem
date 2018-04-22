"""Main point of entrance to the application"""
import sys

from .core import test_execution
from .core.settings_manager import get_global_settings
from .cli import argument_parser, commands


def execute_from_command_line(root_path):
    # deactivate .pyc extention file generation
    sys.dont_write_bytecode = True
    sys.path.insert(0, '')

    # set test_execution values
    test_execution.root_path = root_path
    test_execution.settings = get_global_settings(root_path)

    parser = argument_parser.get_parser()
    args = parser.parse_args()
    commands.command_dispatcher(args)

