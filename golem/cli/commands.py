import os
import sys

import webdriver_manager

import golem
from golem.core import errors
from golem.core import session
from golem.core import settings_manager
from golem.core import suite as suite_module
from golem.core import test
from golem.core import test_directory
from golem.core import utils
from golem.core.project import Project, create_project
from golem.core.settings_manager import get_global_settings
from golem.execution_runner import interactive as interactive_module
from golem.execution_runner.execution_runner import ExecutionRunner
from golem.gui.user_management import Users
from golem.gui import gui_start
from . import messages


def command_dispatcher(args, testdir):
    # Use --golem-dir arg if set
    if args.golem_dir is not None:
        testdir = os.path.abspath(args.golem_dir)
    session.testdir = testdir
    # Insert the golem testdir into sys.path to allow imports
    # from the root of this dir when cwd is not this dir
    sys.path.insert(1, testdir)
    session.testdir = testdir

    if args.help:
        display_help(args.help, args.command)
    elif args.command is None:
        if args.version:
            display_version()
        else:
            print(messages.USAGE_MSG)
    else:
        # It needs a valid Golem test directory from now on
        if not test_directory.is_valid_test_directory(testdir):
            sys.exit(errors.invalid_test_directory.format(testdir))
        # Read global settings
        session.settings = get_global_settings()
        if args.command == 'run':
            run_command(args.project, args.test_query, args.browsers, args.processes, args.environments,
                        args.interactive, args.timestamp, args.report, args.report_folder, args.report_name,
                        args.tags, args.cli_log_level, args.test_functions)
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


def run_command(project='', test_query='', browsers=None, processes=1, environments=None, interactive=False,
                timestamp=None, reports=None, report_folder=None, report_name=None, tags=None,
                cli_log_level=None, test_functions=None):

    if project:
        if test_directory.project_exists(project):
            execution_runner = ExecutionRunner(project, browsers, processes, environments,
                                               interactive, timestamp, reports,
                                               report_folder, report_name,
                                               tags, test_functions)

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
                        msg = (f'golem run: error: the value {test_query} does not match '
                               'an existing test, suite or directory')
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
            sys.exit(f'golem run: error: the project {project} does not exist')
    elif interactive:
        interactive_module.interactive(session.settings, browsers)
    else:
        print(messages.RUN_USAGE_MSG)
        print('Projects:')
        for project in test_directory.get_projects():
            print(f'  {project}')


def gui_command(host=None, port=5000, debug=False):
    gui_start.run_gui(host, port, debug)


def createproject_command(project):
    if test_directory.project_exists(project):
        m = f'golem createproject: error: a project with name \'{project}\' already exists'
        sys.exit(m)
    else:
        create_project(project)


def createtest_command(project, test_name):
    if not test_directory.project_exists(project):
        msg = f'golem createtest: error: a project with name {project} does not exist'
        sys.exit(msg)
    test_name = test_name.replace(os.sep, '.')
    errors = test.create_test(project, test_name)
    if errors:
        sys.exit('golem createtest: error: {}'.format(' '.join(errors)))


def createsuite_command(project, suite_name):
    if not test_directory.project_exists(project):
        msg = f'golem createsuite: error: a project with name {project} does not exist'
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
            print(f'Error: {error}')
        exit(1)
    else:
        print(f'Superuser {username} was created successfully.')


def createdirectory_command(dir_name, no_confirm=False, download_drivers=True):
    """Create a new Golem test directory

    dir_name must be an absolute or relative path.
    If the path exists and is not empty and no_confirm
    is False the user will be prompted to continue.
    """
    abspath = os.path.abspath(dir_name)
    if os.path.isdir(abspath) and os.listdir(abspath):
        # directory is not empty
        if not no_confirm:
            msg = f'Directory {dir_name} is not empty, continue? [Y/n]'
            if not utils.prompt_yes_no(msg):
                return
        if os.path.isfile(os.path.join(abspath, '.golem')):
            sys.exit('Error: target directory is already an existing Golem test directory')
    session.testdir = abspath
    test_directory.create_test_directory(abspath)

    print(f'New golem test directory created at {abspath}')
    print('Use these credentials to access the GUI module:')
    print('  user:     admin')
    print('  password: admin')

    if download_drivers:
        drivers_folder = os.path.join(abspath, 'drivers')
        update = True
        # Download ChromeDriver
        if not no_confirm:
            msg = 'Would you like to download ChromeDriver now? [Y/n]'
            update = utils.prompt_yes_no(msg, True)
        if update:
            webdriver_manager.update('chrome', drivers_folder)
        update = True
        # Download GeckoDriver
        if not no_confirm:
            msg = 'Would you like to download GeckoDriver now? [Y/n]'
            update = utils.prompt_yes_no(msg, True)
        if update:
            webdriver_manager.update('geckodriver', drivers_folder)


def display_version():
    print(f'Golem version {golem.__version__}')
