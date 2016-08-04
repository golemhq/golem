import argparse


def get_golem_parser():
    '''parser of comand line arguments for golem (main program)'''
    
    parser = argparse.ArgumentParser(
        description = 'run a test case, a test suite or start the Golem GUI tool',
        usage = 'golem run project_name test_case|test_suite [-d driver]',
        add_help=False)

    parser.add_argument(
        'action',
        metavar='action',
        help="main action")
    parser.add_argument(
        'project',
        metavar='project',
        nargs='?',
        help="project name",
        default='')
    parser.add_argument(
        'test_or_suite',
        metavar='test_or_suite',
        nargs='?',
        help="test case or test suite to execute",
        default='')
    parser.add_argument(
        '-d',
        '--driver',
        metavar='driver',
        default='firefox',
        choices=['firefox', 'chrome', 'ie', 'phantomjs'],
        help="driver name, options: ['firefox', 'chrome', 'ie', 'phantomjs']")
    '''parser.add_argument(
        '-e',
        '--engine',
        metavar='engine',
        default='selenium',
        help='automation engine')'''
    parser.add_argument(
        '-s',
        '--suite',
        action='store_true',
        help='is suite rather than single test')

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