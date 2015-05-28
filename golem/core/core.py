from golem.core import utils

import traceback


def execute_test_case(test_case, context):

    #get test case data
    test_case_data = utils.get_test_data(context.project, test_case)

    #Create log file
    logf = open('projects\\{0}\\logs\\{1}_{2}.txt'.format(context.project, test_case, utils.get_current_time()), 'w')

    #run test case for each row in test data
    for data_row in test_case_data:

        ###SETUP

        logf.write(utils.get_current_time() + ': Test Start\n')
        logf.write(utils.get_current_time() + ': Test Data: ' + str(data_row) + '\n')
        print 'Executing test case \'%s\'' % test_case       

        #get test case class
        test_class = utils.get_test_case_class(context.project, test_case)

        ###EXECUTE TEST
        try:
            instance = test_class(data_row, context)
        except Exception as ex:
            print ex 

        #check if instance has setup method
        if setup in instance:
            print "instance has setup"

        #check if instance has test method
        if test in instance:
            print "instance has test"
            #instance.run()
        
        try:
            #instance.test()
            print 'Test result: PASS'
            logf.write(utils.get_current_time() + ': Test Result: PASSED\n')
        except Exception as ex:
            template = "An exception of type {0} occured. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print message
            print 'Test result: FAILED'
            print traceback.format_exc()
            logf.write(utils.get_current_time() + ': Test Result: FAILED\n')

        #check if instance has teardown method
        if teardown in instance:
            print "instnace has teardown"

        ###TEAR DOWN

       

    #Close log file
    logf.close()

def execute_test_suite(project, suite, driver, settings):

    tests = utils.get_suite_test_cases(project, suite)

    print 'Executing suite \'%s\' (%i test cases)' % (suite, len(tests))

    for test in tests:
        execute_test_case(project, test, driver, settings)

