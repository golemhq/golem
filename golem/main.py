"""Main point of entrance to the application"""

import argparse
from .core import utils, test_execution
from . import commands


def execute_from_command_line(root_path):
    parser = argparse.ArgumentParser(
        description='run test case, test suite or start the Golem GUI tool',
        usage='golem run project_name test_case|test_suite',
        add_help=False
    )

    sub_parsers = parser.add_subparsers(dest="main_action")
    commands.init_cli(parser, sub_parsers)
    args = parser.parse_args()

    # set test_execution values
    test_execution.root_path = root_path
    test_execution.settings = utils.get_global_settings()

    import golem.core
    golem.core.temp = test_execution.settings

    if args.main_action:
        commands.run(args.main_action, test_execution, args)
