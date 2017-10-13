import os

from golem.core import (utils,
                        test_case,
                        settings_manager,
                        suite as suite_module)
from golem.test_runner import start_execution
from golem.gui import gui_start


class BaseCommand:
    cmd = None

    def __init__(self, parser, subparser):
        cmd_parser = subparser.add_parser(self.cmd)
        self.add_arguments(cmd_parser)
        self._parser = parser

    def add_arguments(self, parser):
        pass

    def run(self, *args):
        raise NotImplementedError('Command not implemented')


class CommandException(Exception):
    pass


class RunCommand(BaseCommand):
    cmd = 'run'

    def add_arguments(self, parser):
        browser_choices = ['firefox',
                          'chrome',
                          'chrome-remote',
                          'chrome-headless',
                          'chrome-remote-headless',
                          'firefox-remote',
                          'ie',
                          'ie-remote']
        parser.add_argument('project', default='',
                            nargs='?', help="project name")
        parser.add_argument('test_or_suite', nargs='?',
                            default='', metavar='test case or suite',
                            help="test case or test suite to run")
        parser.add_argument('-t', '--threads', action='store',
                            nargs='?', default=0, type=int,
                            metavar='amount of threads for parallel execution',
                            help="amount of threads for parallel execution")
        parser.add_argument('-b', '--browsers', action='store',
                            nargs='*', help="Which browsers to use",
                            type=str, metavar='Browser(s)',
                            default=[])
        parser.add_argument('-e', '--environments', action='store',
                            nargs='*',type=str,
                            metavar='Environment(s)',
                            default=[], help="Environments")
        parser.add_argument('--timestamp', action='store', nargs='?', type=str,
                            metavar='Timestamp', help="Timestamp")
        parser.add_argument('-i', '--interactive', action='store_true', default=False,
                            help="Interactive mode")

    def run(self, test_execution, args):
        test_execution.thread_amount = args.threads
        test_execution.cli_drivers = args.browsers
        test_execution.cli_environments = args.environments
        test_execution.timestamp = args.timestamp
        test_execution.interactive = args.interactive

        root_path = test_execution.root_path
        if args.project and args.test_or_suite:

            if not args.project in utils.get_projects(root_path):
                msg = ['Error: the project {0} does not exist'.format(args.project),
                       '',
                       'Usage:', self._parser.usage,
                       '',
                       'Projects:']
                for proj in utils.get_projects(root_path):
                    msg.append('  {}'.format(proj))
                raise CommandException('\n'.join(msg))
            else:
                test_execution.project = args.project
                test_execution.settings = settings_manager.get_project_settings(root_path, args.project)
                if utils.test_suite_exists(root_path, test_execution.project,
                                           args.test_or_suite):
                    test_execution.suite = args.test_or_suite
                    # execute test suite
                    start_execution.run_test_or_suite(root_path,
                                                      test_execution.project,
                                                      suite=test_execution.suite)
                elif utils.test_case_exists(root_path, test_execution.project,
                                            args.test_or_suite):
                    test_execution.test = args.test_or_suite
                    # execute test case
                    start_execution.run_test_or_suite(root_path,
                                                      test_execution.project,
                                                      test=test_execution.test)
                else:
                    # test_or_suite does not match any existing suite or test
                    msg = [('Error: the value {0} does not match an existing '
                            'suite or test'.format(args.test_or_suite)),
                            '',
                            'Usage:', self._parser.usage]
                    raise CommandException('\n'.join(msg))

        elif not args.project and not args.test_or_suite and test_execution.interactive:
            from golem.test_runner import interactive
            interactive.interactive(test_execution.settings, test_execution.cli_drivers)

        elif not args.project:
            msg = ['Usage:',
                   self._parser.usage,
                   '',
                   'Projects:']
            for proj in utils.get_projects(root_path):
                msg.append('  {}'.format(proj))
            raise CommandException('\n'.join(msg))

        elif args.project and not args.test_or_suite:
            msg = ['Usage: {}'.format(self._parser.usage),
                   '',
                   'Test Cases:']
            print('\n'.join(msg))
            test_cases = utils.get_test_cases(root_path,
                                              args.project)
            utils.display_tree_structure_command_line(test_cases['sub_elements'])
            print('\nTest Suites:')
            test_suites = utils.get_suites(root_path, args.project)
            for suite in test_suites['sub_elements']:
                print('  ' + suite['name'])
            raise CommandException()
        else:
            # test_or_suite does not match any existing suite or test
            raise CommandException(
                'Error: the value {0} does not match an existing '
                'suite or test'.format(args.test_or_suite))


class GuiCommand(BaseCommand):
    cmd = 'gui'

    def add_arguments(self, parser):
        parser.add_argument('-p', '--port', action='store',
                            nargs='?', default=5000, type=int,
                            metavar='port number',
                            help="port number to use for Golem GUI")
        # parser.add_argument('-o', '--open', action='store_true',
        #                     default=False,
        #                     help="Open the GUI module in the browser")
        # parser.add_argument('-d', '--debug', action='store_true',
        #                     default=False,
        #                     help="Start the gui application in debug mode")

    def run(self, test_execution, args):
        port_number = args.port
        # debug = args.debug
        # Note, some features won't work if the golem gui is not
        # started with debug = True
        debug = True
        gui_start.run_gui(port_number)


class CreateProjectCommand(BaseCommand):
    cmd = 'createproject'

    def add_arguments(self, parser):
        parser.add_argument('project', help="project name")

    def run(self, test_execution, args):
        root_path = test_execution.root_path

        if args.project in utils.get_projects(root_path):
            msg = 'Error: a project with the name \'{}\' already exists'.format(
                args.project
            )
            raise CommandException(msg)
        # elif args.project == 'demo':
        #     utils.create_demo_project(root_path)
        else:
            utils.create_new_project(root_path, args.project)


class CreateTestCommand(BaseCommand):
    cmd = 'createtest'

    def add_arguments(self, parser):
        parser.add_argument('project', help="project name")
        parser.add_argument('test', metavar='test case name',
                            help="test case name")

    def run(self, test_execution, args):
        root_path = test_execution.root_path

        if args.project not in utils.get_projects(root_path):
            raise CommandException(
                'Error: a project with that name does not exist'
            )
        dot_path = args.test.split('.')
        test_name = dot_path.pop()
        errors = test_case.new_test_case(root_path, args.project,
                                         dot_path, test_name)
        if errors:
            raise CommandException('\n'.join(errors))


class CreateSuiteCommand(BaseCommand):
    cmd = 'createsuite'

    def add_arguments(self, parser):
        parser.add_argument('project', help="project name")
        parser.add_argument('suite', metavar='suite name',
                            help="suite name")

    def run(self, test_execution, args):
        if args.project not in utils.get_projects(
                test_execution.root_path):
            raise CommandException(
                'Error: a project with that name does not exist')
        errors = suite_module.new_suite(test_execution.root_path,
                                        args.project, args.suite)
        if errors:
            raise CommandException('\n'.join(errors))


class CreateUserCommand(BaseCommand):
    cmd = 'createuser'

    def add_arguments(self, parser):
        parser.add_argument('username', help="username")
        parser.add_argument('password', help="suite name")
        parser.add_argument('-a', '--admin', action='store_true',
                            default=False, help="is admin")
        parser.add_argument('-p', '--projects', nargs='+', default=[],
                            help="projects the user has access")
        parser.add_argument('-r', '--reports', nargs='+', default=[],
                            help="reports the user has access")

    def run(self, test_execution, args):
        errors = utils.create_user(test_execution.root_path, args.username,
                                   args.password, args.admin,
                                   args.projects, args.reports)
        if errors:
            raise CommandException('\n'.join(errors))
        else:
            print('User {} was created successfully'.format(args.username))


class CreateDirAdminCommand(BaseCommand):
    cmd = 'createdirectory'

    def add_arguments(self, parser):
        parser.add_argument('name', metavar='name',
                            help='directory name')

    def run(self, args):
        # Generate a new 'golem' directory
        dir_name = args.name

        if os.path.exists(dir_name):
            raise CommandException(
                'Error: the directory {} already exists'.format(dir_name)
            )

        destination = os.path.join(os.getcwd(), dir_name)
        utils.create_test_dir(destination)
