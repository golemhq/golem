"""Main point of entrance to the application"""

import argparse
from .core import test_execution
from .core.settings_manager import get_global_settings
from . import commands


def execute_from_command_line(root_path):
    parser = argparse.ArgumentParser(
        description='run test case, test suite or start the Golem GUI tool',
        usage='golem.py run project test_case|test_suite|directory',
        add_help=False
    )
    sub_parsers = parser.add_subparsers(dest="main_action")
    commands.init_cli(parser, sub_parsers)
    args = parser.parse_args()

    # set test_execution values
    test_execution.root_path = root_path
    test_execution.settings = get_global_settings(root_path)

    import golem.core
    golem.core.temp = test_execution.settings

    if args.main_action:
        commands.run(args.main_action, test_execution, args)
