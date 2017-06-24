from .base import (CommandException, RunCommand,
                   GuiCommand, CreateProjectCommand,
                   CreateSuiteCommand, CreateTestCommand,
                   CreateUserCommand, CreateDirAdminCommand)


INIT_CMDS = [
    RunCommand,
    GuiCommand,
    CreateProjectCommand,
    CreateSuiteCommand,
    CreateTestCommand,
    CreateUserCommand
]


INIT_ADMIN_CMDS = [
    CreateDirAdminCommand
]


COMMANDS = {
}


COMMANDS_ADMIN = {
}


def register_command(klass, parser, subparser):
    COMMANDS[klass.cmd] = klass(parser, subparser)


def register_admin_command(klass, parser, subparser):
    COMMANDS_ADMIN[klass.cmd] = klass(parser, subparser)


def init_cli(parser, subparser):
    for cmd in INIT_CMDS:
        register_command(cmd, parser, subparser)


def init_admin_cli(parser, subparser):
    for cmd in INIT_ADMIN_CMDS:
        register_admin_command(cmd, parser, subparser)


def run(cmd_name, tex, args):
    try:
        cmd = COMMANDS[cmd_name]
        cmd.run(tex, args)
    except CommandException as ex:
        print(str(ex))


def run_admin(cmd_name, args):
    try:
        cmd = COMMANDS_ADMIN[cmd_name]
        cmd.run(args)
    except CommandException as ex:
        print(str(ex))
