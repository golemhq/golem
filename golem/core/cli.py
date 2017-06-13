"""Define the parsers for the golem_admin and main modules"""
import argparse


def get_golem_admin_parser():
    '''parser of comand line arguments for golem-admin script'''

    parser = argparse.ArgumentParser(add_help=False)

    sub_parsers = parser.add_subparsers(dest="main_action")

    new_directory_parser = sub_parsers.add_parser('createdirectory')
    new_directory_parser.add_argument('name', metavar='name', help="directory name")

    return parser
