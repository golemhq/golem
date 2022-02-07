"""Main point of entrance to the application"""
import sys

from .cli import argument_parser, commands


def execute_from_command_line(testdir):
    # deactivate .pyc extention file generation
    sys.dont_write_bytecode = True

    args = argument_parser.get_parser().parse_args()

    commands.command_dispatcher(args, testdir)
