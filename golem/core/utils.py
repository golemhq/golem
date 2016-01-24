from selenium import webdriver
import os, sys, csv, logging, importlib, datetime
from golem.core import test_execution


def get_driver_DEPRECADO(driver_selected):
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
    with file('projects\\%s\\test_cases\\%s.py' % (selected_project, selected_test_case)) as f: #fix use os.path.join
        for line in f:
            t.append(line.strip())
    
    #fix test step format will change

    #get all the steps into a dict
    ###test_case_raw = t[t.index('#steps')+1:t.index('#/steps')]
    
    #parse lines and separate each line into a sub-dict
    # for line in test_case_raw:
    #     #assert lines do not have 4 columns,
    #     if 'assert' in line:
    #         new_line = [line.partition(' ')[0],line.partition(' ')[2],'','']
    #     else:
    #         new_line = [
    #             line.split('.')[0],
    #             line.split('.')[1],
    #             line.split('.')[2].split('(')[0],
    #             line.split('(')[1].replace(')','').replace('"','')] #magic for getting the argument without "" if there is any, * magic *
    #     test_case.append(new_line)

    #return test_case
    return t


def get_suite_test_cases(project, suite):
    ''''''
    tests = list()

    suite_module = importlib.import_module('projects.{0}.test_suites.{1}'.
        format(project, suite), package=None)
    tests = suite_module.test_case_list

    return tests





# def get_test_case_class(project, test):
#     '''returns the test case class (located in
#         root\\projects\\{project_name}\\test_cases\\{test_case_name.py}'''

#     modulex = importlib.import_module('projects.{0}.test_cases.{1}'.format(project, test), package=None)
#     return getattr(modulex, test)

def get_test_case_class(project_name, test_case_name):
    ''' returns the class of a module with unfixed amount of 
    dot separations '''

    # TODO verify the file exists before trying to import

    modulex = importlib.import_module(
        'projects.{}.test_cases.{}'.format(project_name, test_case_name),
        package=None)

    return getattr(modulex, test_case_name)





def get_global_settings():
    '''get global settings from root folder'''

    settings = {}
    if os.path.exists('settings.conf'):
        execfile("settings.conf", settings)
        settings.pop("__builtins__", None) #remove __builtins__ key, not necesary
    else:
        logging.warning('Global Settings file is not present')

    return settings


def get_project_settings(project, global_settings):
    '''get project level settings from selected project folder,
    overrides any global settings'''

    project_settings = {}
    if os.path.exists('projects\\{0}\\project_settings.conf'.format(project)):
        execfile('projects\\{0}\\project_settings.conf'.format(project), project_settings)
        project_settings.pop("__builtins__", None) #remove __builtins__ key, not necesary
    else:
        logging.warning('Project Settings file is not present')
    for setting in project_settings:
        if setting in global_settings:
            global_settings[setting] = project_settings[setting]
        else:
            global_settings[setting] = project_settings[setting]

    return global_settings

    
def run_gui():
    from golem import gui

    gui.root_path = test_execution.root_path

    gui.app.run(debug=True, host='0.0.0.0', port=5000)


def get_current_time():
    time_format = "%Y-%m-%d-%H.%M.%S"
    return datetime.datetime.today().strftime(time_format)


def create(name, source, destination):

    import shutil

    src = source
    dst = destination
    
    
    if name == 'demo':
        for file in os.listdir(src):
            path = os.path.join(src, file)
            shutil.move(path, dst)
    else:
        print


def is_test_suite(project, test_case_or_suite):
    suites = get_suites(project)
    if test_case_or_suite in suites:
        return True
    else:
        return False
