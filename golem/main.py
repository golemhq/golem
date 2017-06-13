"""Main point of entrance to the application"""

import os
import sys

from .core import utils, cli, test_runner, test_execution
from .gui import gui_start, test_case
from .gui import suite as suite_module
from . import commands


def execute_from_command_line(root_path):

    parser = cli.get_golem_parser()
    args = parser.parse_args()

    # set test_execution values
    test_execution.root_path = root_path
    test_execution.settings = utils.get_global_settings()

    import golem.core
    golem.core.temp = test_execution.settings

    commands.run(test_execution, args.main_action)
