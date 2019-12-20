import argparse


def get_parser():
    parser = argparse.ArgumentParser(prog='golem', add_help=False)
    parser.add_argument('-h', '--help', nargs='?', const=True, default=False)
    parser.add_argument('--golem-dir', type=str)
    parser.add_argument('-v', '--version', action='store_true', default=False)
    subparsers = parser.add_subparsers(dest='command')

    # run
    report_choices = ['junit', 'html', 'html-no-images', 'json']
    parser_run = subparsers.add_parser('run', add_help=False)
    parser_run.add_argument('project', nargs='?', default='')
    parser_run.add_argument('test_query', nargs='?', default='')
    parser_run.add_argument('-b', '--browsers', nargs='*', default=[], type=str)
    parser_run.add_argument('-p', '--processes', nargs='?', default=1, type=int)
    parser_run.add_argument('-e', '--environments', nargs='+', default=[], type=str)
    parser_run.add_argument('-t', '--tags', nargs='*', default=[], type=str)
    parser_run.add_argument('-i', '--interactive', action='store_true', default=False)
    parser_run.add_argument('-r', '--report', nargs='+', choices=report_choices,
                            default=[], type=str)
    parser_run.add_argument('--report-folder', nargs='?', type=str)
    parser_run.add_argument('--report-name', nargs='?', type=str)
    parser_run.add_argument('--timestamp', nargs='?', type=str)
    parser_run.add_argument('-l', '--cli-log-level')
    parser_run.add_argument('-h', '--help', action='store_true')

    # gui
    parser_gui = subparsers.add_parser('gui', add_help=False)
    parser_gui.add_argument('--host', action='store', nargs='?', default=None)
    parser_gui.add_argument('-p', '--port', action='store', nargs='?', default=5000, type=int)
    parser_gui.add_argument('-d', '--debug', action='store_true', default=False)
    parser_gui.add_argument('-h', '--help', action='store_true')

    # createproject
    parser_createproject = subparsers.add_parser('createproject', add_help=False)
    parser_createproject.add_argument('project')
    parser_createproject.add_argument('-h', '--help', action='store_true')

    # createtest
    parser_createtest = subparsers.add_parser('createtest', add_help=False)
    parser_createtest.add_argument('project')
    parser_createtest.add_argument('test')
    parser_createtest.add_argument('-h', '--help', action='store_true')

    # createsuite
    parser_createsuite = subparsers.add_parser('createsuite', add_help=False)
    parser_createsuite.add_argument('project')
    parser_createsuite.add_argument('suite')
    parser_createsuite.add_argument('-h', '--help', action='store_true')

    # createsuperuser
    subparsers.add_parser('createuser', add_help=False)

    # createsuperuser
    parser_createsuperuser = subparsers.add_parser('createsuperuser', add_help=False)
    parser_createsuperuser.add_argument('-u', '--username')
    parser_createsuperuser.add_argument('-e', '--email')
    parser_createsuperuser.add_argument('-p', '--password')
    parser_createsuperuser.add_argument('-n', '--noinput', action='store_true', default=False)
    parser_createsuperuser.add_argument('-h', '--help', action='store_true')

    return parser


def get_admin_parser():
    parser = argparse.ArgumentParser(prog='golem-admin', add_help=False)
    parser.add_argument('-h', '--help', nargs='?', const=True, default=False)
    subparsers = parser.add_subparsers(dest='command')
    
    # createdirectory
    parser_createdirectory = subparsers.add_parser('createdirectory', add_help=False)
    parser_createdirectory.add_argument('name')
    parser_createdirectory.add_argument('-y', '--yes', action='store_true',
                                        default=False, dest='no_confirm')
    parser_createdirectory.add_argument('-h', '--help', action='store_true')
    
    return parser
