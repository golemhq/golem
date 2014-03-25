from golem.core import utils


def execute_test_case(project, test_case, driver_selected, settings):

    #exec('import %s.test_cases.%s' % (args.project, test_case_selected)) #module = __import__(module_name) #class_ = getattr(module, class_name) #instance = class_()

    #get test data
    data_dict_list = utils.get_test_data(project, test_case)

    #Create log file
    logf = open('projects\\%s\\logs\\%s - %s.txt' % (project, test_case, utils.get_current_time()), 'w')

    #run test case for each row in test data
    for data_dict in data_dict_list:

        ###SETUP
        #get driver browser instance
        driver = utils.get_driver(driver_selected)

        driver.maximize_window() #improve parameterize?





        logf.write(utils.get_current_time() + ': Test Start\n')
        logf.write(utils.get_current_time() + ': Test Data: ' + str(data_dict) + '\n')
        print 'Executing test case \'%s\'' % test_case

        #set implicit wait
        if 'implicit_wait' in settings: driver.implicitly_wait(settings['implicit_wait']) #default is 0

        #get test case class
        test_class = utils.get_test_case_class(project, test_case)

        ###EXECUTE TEST

        try:
            instance = test_class(driver, data_dict)
            print 'Test result: PASS'
            logf.write(utils.get_current_time() + ': Test Result: PASSED\n')
        except Exception as ex:
            template = "An exception of type {0} occured. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print message
            print 'Test result: FAILED'
            logf.write(utils.get_current_time() + ': Test Result: FAILED\n')


        ###TEAR DOWN

        driver.quit()

    #Close log file
    logf.close()

def execute_test_suite(project, suite, driver, settings):

    tests = utils.get_suite_test_cases(project, suite)

    print 'Executing suite \'%s\' (%i test cases)' % (suite, len(tests))

    for test in tests:
        execute_test_case(project, test, driver, settings)

