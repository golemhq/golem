from golem.core import utils, core

import sys, os


def execute_from_command_line(root):

    parser = utils.get_parser()
    args = parser.parse_args()

    #set test context values
    test_context = utils.Test_context(
        root=root,
        project=args.project,
        test_case=args.test,
        engine=args.engine,
        selenium_driver=args.driver)

    #get global settings
    test_context.settings = utils.get_global_settings()

    #if action is gui, launch golem gui
    if args.action == 'gui':
        utils.run_gui()
        sys.exit()

    #check if project parameter is not present      ##this cannot happen
    if not test_context.project:
        print 'Usage:', parser.usage
        print '\nProject List:'
        for proj in utils.get_projects():
            print '> ' + proj
        sys.exit()

    if args.action == 'run':
        #check if selected project does not exists
        if not os.path.isdir('projects\\{0}'.format(test_context.project)):
            sys.exit('ERROR: the project {0} does not exist'.format(test_context.project))
        else:
        #get project settings (override settings already present in global settings)
            test_context.settings = utils.get_project_settings(
                test_context.project, 
                test_context.settings)

        #check if test parameter is not present
        if test_context.test_case == '':
            print 'Usage:', parser.usage
            print
            print 'Test Case List:'
            for tc in utils.get_test_cases(test_context.project):
                print '> ' + tc
            print
            print 'Test Suite List:'
            for ts in utils.get_suites(test_context.project):
                print '> ' + ts
            sys.exit()

        #check if test case exists and run it
        if os.path.exists('projects\\{0}\\test_cases\\{1}.py'.format(test_context.project, test_context.test_case)):
            core.execute_test_case( 
                test_context.test_case,
                test_context)
        #check if test suite exists and run it
        elif os.path.exists('projects\\{0}\\test_suites\\{1}.py'.format(test_context.project, test_context.test_case)):
            core.execute_test_suite(
                test_context.project,
                test_context.test_case,
                test_context.selenium_driver,
                test_context.settings)
        else:
            sys.exit("ERROR: no test case or suite named %s exists" % test)


if __name__ == "__main__":

    execute_from_command_line()