from selenium import webdriver
import os, sys, csv, warnings, argparse, importlib

def get_driver(driver_selected):
    driver = None

    if driver_selected == 'firefox':
        driver = webdriver.Firefox()
    if driver_selected == 'chrome':
        driver = webdriver.Chrome()
    if driver_selected == 'ie':
        driver = webdriver.Ie()
    if driver_selected == 'phantomjs':
        if os.name == 'nt':
            a = os.path.dirname(os.path.abspath(__file__))
            b = os.path.abspath(os.path.join( a , os.pardir))
            driver = webdriver.PhantomJS(executable_path= b + '\\lib\\phantom\\phantomjs.exe')
        else:
            print 'not implemented yet'
            sys.exit()

    return driver


def get_test_data(project, test_case):
    ''''''
    data_dict_list = list()

    #check if there is a data file
    #Check if CSV file == test case name exists
    if os.path.exists('projects\\%s\\data\\%s.csv' % (project, test_case)):
        ##Read CSV: ##http://courses.cs.washington.edu/courses/cse140/13wi/csv-parsing.html
        f = open('projects\\%s\\data\\%s.csv' % (project, test_case), 'rb') # opens the csv file
        dict_reader = csv.DictReader(f)  # creates DictReader (list of dictionaries)
        for row in dict_reader:
            data_dict_list.append(row)
        f.close()
    else:
        data_dict_list = list([{'empty':True}])
        print 'No data file found'

    return data_dict_list


def get_projects():
    projects = list()
    projects = os.walk('projects').next()[1]
    return projects


def get_test_cases(selected_project):
    test_cases = list()

    for (dirpath, dirnames, filenames) in os.walk('projects\\%s\\test_cases' % selected_project):
        test_cases.extend(filenames)
    test_cases.remove('__init__.py')

    for (i, tc) in enumerate(test_cases):
        test_cases[i] = tc[:-3]

    return test_cases


def get_suites(selected_project):
    test_suites = list()

    for (dirpath, dirnames, filenames) in os.walk('projects\\%s\\test_suites' % selected_project):
        test_suites.extend(filenames)
        break
    test_suites.remove('__init__.py')

    for (i, tc) in enumerate(test_suites):
        test_suites[i] = tc[:-3]

    return test_suites


def get_selected_test_case(selected_project, selected_test_case):
    '''retrieves the selected test case of the selected project, returns a list
    of lists, where each list is a test case step, and each sublist element is
    a step component ('page','test_object', 'action', etc) '''

    test_case = list()
    test_case_raw = list()
    t = list()

    #read test_case file
    with file('projects\\%s\\test_cases\\%s.py' % (selected_project, selected_test_case)) as f:
        for line in f:
            t.append(line.strip())
    #get all the steps into a dict
    test_case_raw = t[t.index('#steps')+1:t.index('#/steps')]
    #parse lines and separate each line into a sub-dict
    for line in test_case_raw:
        #assert lines do not have 4 columns,
        if 'assert' in line:
            new_line = [line.partition(' ')[0],line.partition(' ')[2],'','']
        else:
            new_line = [
                line.split('.')[0],
                line.split('.')[1],
                line.split('.')[2].split('(')[0],
                line.split('(')[1].replace(')','').replace('"','')] #magic for getting the argument without "" if there is any, * magic *
        test_case.append(new_line)

    return test_case


def get_suite_test_cases(project,suite):
    ''''''
    tests = list()

    suite_module = importlib.import_module('projects.%s.test_suites.%s' % (project, suite), package=None)
    tests = suite_module.test_case_list

    return tests


def get_test_case_class(project, test):
    ''''''
    modulex = importlib.import_module('projects.%s.test_cases.%s' % (project, test), package=None)
    return getattr(modulex, 'Testclass')


def get_parser():
    '''parser of comand line arguments'''


    parser = argparse.ArgumentParser(
        description = 'description',
        usage = 'golem project_name test_case|test_suite [-d driver] [-r repeat]')

    parser.add_argument(
        'project',
        metavar='project',
        nargs='?',
        help="project name",
        default='')
    parser.add_argument(
        'test',
        metavar='test',
        nargs='?',
        help="test case or test suite to execute",
        default='')
    parser.add_argument(
        '-d',
        metavar='driver',
        default='firefox',
        choices=['firefox', 'chrome', 'ie', 'phantomjs'],
        help="driver name, options: ['firefox', 'chrome', 'ie', 'phantomjs']")
    parser.add_argument(
        '-r',
        metavar='repeat',
        default=0,
        help='times to repeat test',
        type=int)

    return parser


def get_global_settings():
    '''get global settings from root folder'''

    settings = {}
    if os.path.exists('global_settings.conf'):
        execfile("global_settings.conf", settings)
        settings.pop("__builtins__", None) #remove __builtins__ key, not necesary
    else:
        warnings.warn('Global Settings file is not present')

    return settings


def get_project_settings(project):
    '''get project level settings from selected project folder'''

    settings = {}
    if os.path.exists('project\\%s\\project_settings.confconf' % project):
        execfile('project\\%s\\project_settings.confconf' % project, settings)
    else:
        warnings.warn('Project Settings file is not present')

    return settings


def run_gui():
    import webbrowser
    from multiprocessing import Pool

    os.environ["DJANGO_SETTINGS_MODULE"] = "golem.gui.golem-gui.settings"

    from django.core.management import execute_from_command_line

    pool = Pool(processes=1)

    result = pool.apply_async(execute_from_command_line, [['','runserver']])

    webbrowser.open('http://localhost:8000')

    raw_input()





def get_current_time():
        import datetime
        time_format = "%Y-%m-%d-%H.%M.%S"
        return datetime.datetime.today().strftime(time_format)


def create(action):
    print 'demo location'
    print 'destination'