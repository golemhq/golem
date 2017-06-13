"""Main point of entrance to the application"""

from .core import utils, cli, test_execution
from . import commands


def execute_from_command_line(root_path):

    parser = cli.get_golem_parser()
    args = parser.parse_args()

    # set test_execution values
    test_execution.root_path = root_path
    test_execution.settings = utils.get_global_settings()

    import golem.core
    golem.core.temp = test_execution.settings

    commands.run(test_execution, args.main_action, args)
