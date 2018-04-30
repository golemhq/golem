import os
import sys

from golem.core import (utils,
                        test_execution,
                        suite as suite_module,
                        test_case,
                        settings_manager)
from golem.gui import gui_start
from golem.test_runner import start_execution

from .argument_parser import get_parser
from . import messages


def command_dispatcher(args):
    if args.help:
        display_help(args.help, args.command)
    elif args.command == 'run':
        run_command(args.project, args.test_or_suite,
                    args.browsers, args.threads,
                    args.environments, args.interactive,
                    args.timestamp)
    elif args.command == 'gui':
        gui_command(args.port)
    elif args.command == 'createproject':
        createproject_command(args.project)
    elif args.command == 'createtest':
        createtest_command(args.project, args.test)
    elif args.command == 'createsuite':
        createsuite_command(args.project, args.suite)
    elif args.command == 'createuser':
        createuser_command(args.username, args.password,
                           args.admin, args.projects, args.reports)
    elif args.command == None:
        print(messages.USAGE_MSG)


def display_help(help, command):
    if help == 'run' or command == 'run':
        print(messages.RUN_USAGE_MSG)
    elif help == 'gui' or command == 'gui':
        print(messages.GUI_USAGE_MSG)
    elif help == 'createproject' or command == 'createproject':
        print(messages.CREATEPROJECT_USAGE_MSG)
    elif help == 'createtest' or command == 'createtest':
        print(messages.CREATETEST_USAGE_MSG)
    elif help == 'createsuite' or command == 'createsuite':
        print(messages.CREATESUITE_USAGE_MSG)
    elif help == 'createuser' or command == 'createuser':
        print(messages.CREATEUSER_USAGE_MSG)
    else:
        print(messages.USAGE_MSG)


def run_command(project='', test_or_suite='', browsers=[], threads=1,
                environments=[], interactive=False, timestamp=None):
    test_execution.thread_amount = threads
    test_execution.cli_drivers = browsers
    test_execution.cli_environments = environments
    test_execution.timestamp = timestamp
    test_execution.interactive = interactive
    root_path = test_execution.root_path
    if project:
        existing_projects = utils.get_projects(root_path)
        if project in existing_projects:
            test_execution.project = project
            settings = settings_manager.get_project_settings(root_path, project)
            test_execution.settings = settings
            if test_or_suite:
                if suite_module.suite_exists(root_path, test_execution.project,
                                         test_or_suite):
                    test_execution.suite = test_or_suite
                    # execute test suite
                    start_execution.run_test_or_suite(root_path,
                                                      test_execution.project,
                                                      suite=test_execution.suite)
                elif test_case.test_case_exists(root_path, test_execution.project,
                                                test_or_suite):
                    test_execution.test = test_or_suite
                    # execute test case
                    start_execution.run_test_or_suite(root_path,
                                                      test_execution.project,
                                                      test=test_execution.test)
                else:
                    # TODO run directory
                    # test_or_suite does not match any existing suite or test
                    msg = ('golem run: error: the value {0} does not match an existing '
                           'test or suite'.format(test_or_suite))
                    sys.exit(msg)
            else:
                print(messages.RUN_USAGE_MSG)
                test_cases = utils.get_test_cases(root_path, project)
                print('Test Cases:')
                utils.display_tree_structure_command_line(test_cases['sub_elements'])
                test_suites = utils.get_suites(root_path, project)
                print('\nTest Suites:')
                # TODO print suites in structure
                for suite in test_suites['sub_elements']:
                    print('  ' + suite['name'])
        else:
            msg = ('golem run: error: the project {0} does not exist'.format(project))
            sys.exit(msg)

    elif test_execution.interactive:
        from golem.test_runner import interactive
        interactive.interactive(test_execution.settings, test_execution.cli_drivers)
    else:
        print(messages.RUN_USAGE_MSG)
        print('Projects:')
        for proj in utils.get_projects(root_path):
            print('  {}'.format(proj))


def gui_command(port=5000):
    gui_start.run_gui(port)


def createproject_command(project):
    root_path = test_execution.root_path

    if project in utils.get_projects(root_path):
        msg = ('golem createproject: error: a project with name \'{}\' already exists'
               .format(project))
        sys.exit(msg)
    else:
        utils.create_new_project(root_path, project)


def createtest_command(project, test):
    root_path = test_execution.root_path

    if project not in utils.get_projects(root_path):
        msg = ('golem createtest: error: a project with name {} '
               'does not exist'.format(project))
        sys.exit(msg)
    dot_path = test.split('.')
    test_name = dot_path.pop()
    errors = test_case.new_test_case(root_path, project,
                                     dot_path, test_name)
    if errors:
        sys.exit('golem createtest: error: {}'.format(' '.join(errors)))


def createsuite_command(project, suite_name):
    if project not in utils.get_projects(test_execution.root_path):
        msg = ('golem createsuite: error: a project with name {} '
               'does not exist'.format(project))
        sys.exit(msg)
    errors = suite_module.new_suite(test_execution.root_path,
                             project, [], suite_name)
    if errors:
        sys.exit('golem createsuite: error: {}'.format(' '.join(errors)))


def createuser_command(username, password, is_admin=False,
                       projects=[], reports=[]):
    errors = utils.create_user(test_execution.root_path, username,
                               password, is_admin, projects, reports)
    if errors:
        sys.exit('golem createuser: error: {}'.format(' '.join(errors)))
    else:
        print('User {} was created successfully'.format(username))


def createdirectory_command(dir_name):
    # Generate a new 'golem' directory
    if os.path.exists(dir_name):
        msg = ('golem-admin createdirectory: error: the directory {} '
               'already exists'.format(dir_name))
        sys.exit(msg)
    else:
        destination = os.path.join(os.getcwd(), dir_name)
        utils.create_test_dir(destination)