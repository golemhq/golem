"""A CLI admin script used to generate the initial 'test directory that
contains the projects and all the required fields for Golem to
work. This is a is directory independent script.
"""

import os
import shutil
import sys

import golem
from golem.core import cli, utils


def main():

    parser = cli.get_golem_admin_parser()
    args = parser.parse_args()

    if args.main_action == 'createdirectory':
        # Generate a new 'golem' directory
        dir_name = args.name
        if os.path.exists(dir_name):
            print('Error: the directory {} already exists'.format(dir_name))
        else:
            destination = os.path.join(os.getcwd(), dir_name)
            utils.create_test_dir(destination)
    return
