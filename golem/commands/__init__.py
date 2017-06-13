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


def register_command(klass):
    COMMANDS[klass.cmd] = klass()


def run(cmd_name, tex, args):
    cmd = COMMANDS[cmd]
    cmd_obj = cmd(tex, args)
    cmd_obj.run()
