import os
import sys

from golem.core import (utils,
                        test_execution,
                        suite as suite_module,
                        test_case,
                        settings_manager)
from golem.gui import gui_start
from golem.test_runner.execution_runner import ExecutionRunner
from golem.test_runner import interactive as interactive_module
from . import messages


def command_dispatcher(args):
    if args.help:
        display_help(args.help, args.command)
    elif args.command == 'run':
        run_command(args.project, args.test_query,
                    args.browsers, args.threads,
                    args.environments, args.interactive,
                    args.timestamp, args.report,
                    args.report_folder, args.report_name, args.tags)
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


def run_command(project='', test_query='', browsers=None, processes=1,
                environments=None, interactive=False, timestamp=None,
                reports=None, report_folder=None, report_name=None, tags=None):
    execution_runner = ExecutionRunner(browsers, processes, environments, interactive,
                                       timestamp, reports, report_folder, report_name, tags)
    if project:
        existing_projects = utils.get_projects(test_execution.root_path)
        if project in existing_projects:
            execution_runner.project = project
            settings = settings_manager.get_project_settings(test_execution.root_path,
                                                             project)
            test_execution.settings = settings
            # add --interactive value to settings to make
            # it available from inside a test
            test_execution.settings['interactive'] = interactive
            if test_query:
                if suite_module.suite_exists(test_execution.root_path,
                                             project, test_query):
                    execution_runner.run_suite(test_query)
                elif test_case.test_case_exists(test_execution.root_path,
                                                project, test_query):
                    execution_runner.run_test(test_query)
                else:
                    if test_query == '.':
                        test_query = ''
                    path = os.path.join(test_execution.root_path, 'projects',
                                        project, 'tests', test_query)
                    if os.path.isdir(path):
                        execution_runner.run_directory(test_query)
                    else:
                        msg = ('golem run: error: the value {} does not match '
                               'an existing test, suite or directory'.format(test_query))
                        sys.exit(msg)
            else:
                print(messages.RUN_USAGE_MSG)
                test_cases = utils.get_test_cases(test_execution.root_path, project)
                print('Test Cases:')
                utils.display_tree_structure_command_line(test_cases['sub_elements'])
                test_suites = utils.get_suites(test_execution.root_path, project)
                print('\nTest Suites:')
                # TODO print suites in structure
                for suite in test_suites['sub_elements']:
                    print('  ' + suite['name'])
        else:
            msg = ('golem run: error: the project {} does not exist'.format(project))
            sys.exit(msg)
    elif interactive:
        interactive_module.interactive(test_execution.settings, browsers)
    else:
        print(messages.RUN_USAGE_MSG)
        print('Projects:')
        for project in utils.get_projects(test_execution.root_path):
            print('  {}'.format(project))


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


def createdirectory_command(dir_name, no_confirm=False):
    """Create a new Golem test directory

    dir_name must be an absolute or relative path.
    If the path exists and is not empty and no_confirm
    is False the user will be prompted to continue.
    """
    abspath = os.path.abspath(dir_name)
    if os.path.exists(abspath) and os.listdir(abspath):
        # directory is not empty
        if not no_confirm:
            msg = 'Directory {} is not empty, continue? [Y/n]'.format(dir_name)
            if not utils.prompt_yes_no(msg):
                return
    utils.create_test_dir(abspath)
