from .base import (CommandException, RunCommand,
                   GuiCommand, CreateProjectCommand,
                   CreateSuiteCommand, CreateTestCommand,
                   CreateUserCommand)


COMMANDS = {
    GuiCommand.cmd: GuiCommand,
    CreateProjectCommand.cmd: CreateProjectCommand,
    CreateSuiteCommand.cmd: CreateSuiteCommand,
    CreateTestCommand.cmd: CreateTestCommand,
    CreateUserCommand.cmd: CreateUserCommand
}


COMMANDS_ADMIN = {
    CreateDirAdminCommand.cmd: CreateDirAdminCommand
}


def register_command(klass):
    COMMANDS[klass.cmd] = klass()


def register_admin_command(klass):
    COMMANDS_ADMIN[klass.cmd] = klass()


def run(cmd_name, tex, args):
    cmd = COMMANDS[cmd]
    cmd_obj = cmd(tex, args)
    cmd_obj.run()


def run_admin(cmd_name, args):
    cmd = COMMANDS_ADMIN[cmd]
    cmd_obj = cmd(args)
    cmd_obj.run()
