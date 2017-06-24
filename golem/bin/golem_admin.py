"""A CLI admin script used to generate the initial 'test directory that
contains the projects and all the required fields for Golem to
work. This is a is directory independent script.
"""
import argparse
from .. import commands


def main():
    parser = argparse.ArgumentParser(add_help=False)
    sub_parsers = parser.add_subparsers(dest="main_action")

    commands.init_admin_cli(sub_parsers, sub_parsers)
    args = parser.parse_args()

    if args.main_action:
        commands.run_admin(args.main_action, args)
