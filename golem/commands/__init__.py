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


def register_command(klass, parser):
    COMMANDS[klass.cmd] = klass(parser)


def register_admin_command(klass, parser):
    COMMANDS_ADMIN[klass.cmd] = klass(parser)


def init_cli(parser):
    for cmd in INIT_CMDS:
        register_command(cmd, parser)


def init_admin_cli(parser):
    for cmd in INIT_ADMIN_CMDS:
        register_admin_command(cmd, parser)


def run(cmd_name, tex, args):
    cmd = COMMANDS[cmd_name]
    cmd.run(tex, args)


def run_admin(cmd_name, args):
    cmd = COMMANDS_ADMIN[cmd_name]
    cmd.run(args)
