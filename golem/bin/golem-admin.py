"""A CLI admin script used to generate the initial directory that
contains the projects and all the required fields for Golem to
work. This is a is directory independent script.
"""

import os
import shutil
import sys

import golem
from golem.core import cli, utils


def execute_from_command_line():

    current_directory = os.getcwd()

    parser = cli.get_golem_admin_parser()
    args = parser.parse_args()

    if args.action == 'start':
        # Generate a new 'golem' directory
        dir_name = args.name
        if os.path.exists(dir_name):
            print 'Error: the directory {} already exists'.format(dir_name)
        else:
            # move template directory to new directory
            source = os.path.join(golem.__path__[0], 'template')
            destination = os.path.join(os.getcwd(), dir_name)
            shutil.copytree(source, destination)
    return


if __name__ == "__main__":

    execute_from_command_line()
