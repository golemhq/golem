"""A CLI admin script used to generate the initial test directory that
contains the projects and all the required fields for Golem to
work.
"""
from golem.cli import argument_parser, commands, messages


def main():
    parser = argument_parser.get_admin_parser()
    args = parser.parse_args()
    if args.help:
        print(messages.ADMIN_USAGE_MSG)
    elif args.command:
        if args.command == 'createdirectory':
            commands.createdirectory_command(args.name, args.no_confirm)
    else:
        print(messages.ADMIN_USAGE_MSG)
