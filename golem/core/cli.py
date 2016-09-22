import argparse


def get_golem_parser():
    '''parser of comand line arguments for golem (main program)'''

    parser = argparse.ArgumentParser(
        description='run test case, test suite or start the Golem GUI tool',
        usage='golem run project_name test_case|test_suite',
        add_help=False)

    sub_parsers = parser.add_subparsers(dest="main_action")

    run_parser = sub_parsers.add_parser('run')
    run_parser.add_argument('project',
                            default='',
                            nargs='?',
                            help="project name")
    run_parser.add_argument('test_or_suite',
                            nargs='?',
                            default='',
                            metavar='test case or suite',
                            help="test case or test suite to run")

    gui_parser = sub_parsers.add_parser('gui')

    start_project_parser = sub_parsers.add_parser('startproject')

    createuser_parser = sub_parsers.add_parser('createuser')

    return parser


def get_golem_admin_parser():
    '''parser of comand line arguments for golem-admin script'''

    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument(
        'action',
        metavar='action',
        choices=['start'],
        help="action"
    )
    parser.add_argument(
        'name',
        metavar='name',
        help="directory name"
    )

    return parser
