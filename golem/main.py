"""Main point of entrance to the application"""

import os
import sys

from golem.core import utils, cli, test_runner, test_execution


def execute_from_command_line(root_path):

    parser = cli.get_golem_parser()
    args = parser.parse_args()

    # set test context values

    test_execution.root_path = root_path
    test_execution.project_name = args.project

    # get global settings
    test_execution.settings = utils.get_global_settings()

    # if action is gui, launch golem gui
    if args.action == 'gui':
        utils.run_gui()
        sys.exit()

    # check if project parameter is not present      ##this cannot happen
    if not test_execution.project_name:
        print 'Usage:', parser.usage, '\n\n', 'Project List:'
        for proj in utils.get_projects(root_path):
            print '> {}'.format(proj)
        sys.exit()

    if args.action == 'run':
        # check if selected project does not exist
        if not os.path.isdir(
                os.path.join('projects', test_execution.project_name)):
            sys.exit(
                'ERROR: the project {0} does not exist'
                .format(test_execution.project_name))
        else:
            '''test_context.settings = utils.get_project_settings(
                test_context.project,
                test_context.settings) '''

            if utils.is_test_suite(test_execution.project_name,
                                   args.test_or_suite):
                test_execution.suite_name = args.test_or_suite
            else:
                test_execution.test_name = args.test_or_suite

            # check if test parameter is not present
            if not test_execution.suite_name and not test_execution.test_name:
                print 'Usage:', parser.usage
                print '\nTest Case List:'
                test_cases = utils.get_test_cases(
                                    root_path,
                                    test_execution.project_name)
                utils.display_tree_structure_command_line(test_cases)
                print '\nTest Suite List:'
                for ts in utils.get_suites(test_execution.project_name):
                    print '> ' + ts
                sys.exit()

            if test_execution.suite_name:
                print "is suite!!!"
                test_runner.run_suite(
                    test_execution.project_name,
                    test_execution.suite_name)
            else:
                print "is not suite!!!"

                test_runner.run_single_test_case(
                    test_execution.project_name,
                    test_execution.test_name)
