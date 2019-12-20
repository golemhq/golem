import os
import sys

import golem
from golem.core import (utils, session, suite as suite_module, test,
                        settings_manager, test_directory)
from golem.core.project import Project, create_project
from golem.gui import gui_start
from golem.test_runner.execution_runner import ExecutionRunner
from golem.test_runner import interactive as interactive_module
from golem.gui.user_management import Users
from . import messages


def command_dispatcher(args):
    if args.help:
        display_help(args.help, args.command)
    elif args.command == 'run':
        run_command(args.project, args.test_query, args.browsers, args.processes,
                    args.environments, args.interactive, args.timestamp, args.report,
                    args.report_folder, args.report_name, args.tags, args.cli_log_level)
    elif args.command == 'gui':
        gui_command(args.host, args.port, args.debug)
    elif args.command == 'createproject':
        createproject_command(args.project)
    elif args.command == 'createtest':
        createtest_command(args.project, args.test)
    elif args.command == 'createsuite':
        createsuite_command(args.project, args.suite)
    elif args.command == 'createuser':
        createuser_command()
    elif args.command == 'createsuperuser':
        createsuperuser_command(args.username, args.email, args.password, args.noinput)
    elif args.command is None:
        if args.version:
            display_version()
        else:
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
    elif help == 'createsuperuser' or command == 'createsuperuser':
        print(messages.CREATESUPERUSER_USAGE_MSG)
    else:
        print(messages.USAGE_MSG)


def run_command(project='', test_query='', browsers=None, processes=1,
                environments=None, interactive=False, timestamp=None,
                reports=None, report_folder=None, report_name=None,
                tags=None, cli_log_level=None):
    execution_runner = ExecutionRunner(browsers, processes, environments, interactive,
                                       timestamp, reports, report_folder, report_name, tags)
    if project:
        if test_directory.project_exists(project):
            execution_runner.project = project
            session.settings = settings_manager.get_project_settings(project)
            # add --interactive value to settings to make
            # it available from inside a test
            session.settings['interactive'] = interactive
            # override cli_log_level setting if provided by the CLI
            if cli_log_level:
                session.settings['cli_log_level'] = cli_log_level.upper()
            if test_query:
                norm_query = utils.normalize_query(test_query)
                if suite_module.Suite(project, norm_query).exists:
                    execution_runner.run_suite(norm_query)
                elif test.Test(project, norm_query).exists:
                    execution_runner.run_test(norm_query)
                else:
                    if test_query == '.':
                        test_query = ''
                    path = os.path.join(session.testdir, 'projects',
                                        project, 'tests', test_query)
                    if os.path.isdir(path):
                        execution_runner.run_directory(test_query)
                    else:
                        msg = ('golem run: error: the value {} does not match '
                               'an existing test, suite or directory'.format(test_query))
                        sys.exit(msg)
            else:
                print(messages.RUN_USAGE_MSG)
                tests = Project(project).test_tree
                print('Tests:')
                utils.display_tree_structure_command_line(tests['sub_elements'])
                suites = Project(project).suite_tree
                print('\nTest Suites:')
                # TODO print suites in structure
                for suite in suites['sub_elements']:
                    print('  ' + suite['name'])
        else:
            msg = ('golem run: error: the project {} does not exist'.format(project))
            sys.exit(msg)
    elif interactive:
        interactive_module.interactive(session.settings, browsers)
    else:
        print(messages.RUN_USAGE_MSG)
        print('Projects:')
        for project in test_directory.get_projects():
            print('  {}'.format(project))


def gui_command(host=None, port=5000, debug=False):
    gui_start.run_gui(host, port, debug)


def createproject_command(project):
    if test_directory.project_exists(project):
        msg = ('golem createproject: error: a project with name \'{}\' already exists'
               .format(project))
        sys.exit(msg)
    else:
        create_project(project)


def createtest_command(project, test_name):
    if not test_directory.project_exists(project):
        msg = ('golem createtest: error: a project with name {} '
               'does not exist'.format(project))
        sys.exit(msg)
    test_name = test_name.replace(os.sep, '.')
    errors = test.create_test(project, test_name)
    if errors:
        sys.exit('golem createtest: error: {}'.format(' '.join(errors)))


def createsuite_command(project, suite_name):
    if not test_directory.project_exists(project):
        msg = ('golem createsuite: error: a project with name {} '
               'does not exist'.format(project))
        sys.exit(msg)
    errors = suite_module.create_suite(project, suite_name)
    if errors:
        sys.exit('golem createsuite: error: {}'.format(' '.join(errors)))


# TODO deprecated
def createuser_command():
    sys.exit('Error: createuser command is deprecated. Use createsuperuser instead.')


def createsuperuser_command(username, email, password, no_input=False):
    if no_input:
        if username is None or password is None:
            sys.exit('Error: --username and --password are required for --noinput.')
    else:
        try:
            while True:
                username = input('Username: ').strip()
                if username:
                    break
            while True:
                email = input('Email address (optional): ').strip()
                if email and not utils.validate_email(email):
                    print('Error: Enter a valid email address.')
                else:
                    break
            while True:
                password = input('Password: ')
                repeat_password = input('Password (again): ')
                if not len(password):
                    print('Error: Blank passwords are not allowed.')
                elif password != repeat_password:
                    print('Error: The passwords did not match.')
                else:
                    break
        except KeyboardInterrupt:
            sys.exit('Cancelled.')
    errors = Users.create_super_user(username, password, email)
    if errors:
        for error in errors:
            print('Error: {}'.format(error))
        exit(1)
    else:
        print('Superuser {} was created successfully.'.format(username))


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
        if os.path.isfile(os.path.join(abspath, '.golem')):
            sys.exit('Error: target directory is already an existing Golem test directory')
    session.testdir = abspath
    test_directory.create_test_directory(abspath)
    print('New golem test directory created at {}'.format(abspath))
    print('Use credentials to access the GUI module:')
    print('user: admin')
    print('password: admin')


def display_version():
    print('Golem version {}'.format(golem.__version__))
