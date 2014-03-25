from golem.core import utils, core

import sys, os


def execute_from_command_line():

    parser = utils.get_parser()
    args = parser.parse_args()

    #set global variable values
    project = args.project
    test = args.test
    driver_selected = args.d

    settings = dict()

    #get global settings
    settings = utils.get_global_settings()

    #if action is gui, launch golem gui
    if project == 'gui':
        utils.run_gui()
        sys.exit()

    #check if project parameter is not present
    if project == '':
        print 'Usage:',parser.usage
        print '\nProject List:'
        for proj in utils.get_projects():
            print '> ' + proj
        sys.exit()


    #check if selected project does not exists
    if not os.path.isdir('projects\\%s' % project):
        sys.exit("ERROR: the project %s does not exist" % project)
    #else:
        #get project settings
        #settings = get_project_settings(project)

    #check if test parameter is not present
    if test == '':
        print 'Usage:',parser.usage
        print '\nTest Case List:'
        for tc in utils.get_test_cases(project):
            print '> ' + tc
        print '\nTest Suite List:'
        for ts in utils.get_suites(project):
            print '> ' + ts
        sys.exit()

    #check if test case or test suite exists
    if os.path.exists('projects\\%s\\test_cases\\%s.py' % (project, test)):
        core.execute_test_case(project, test, driver_selected, settings)

    elif os.path.exists('projects\\%s\\test_suites\\%s.py' % (project, test)):
        #test_suite = '%s\\test_suites\\%s.py' % (args.project, args.test)
        core.execute_test_suite(project, test, driver_selected, settings)
    else:
        sys.exit("ERROR: no test case or suite named %s exists" % test)


if __name__ == "__main__":

    execute_from_command_line()