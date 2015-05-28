from selenium import webdriver
import os, sys, csv, logging, argparse, importlib, datetime


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


def get_suite_test_cases(project,suite):
    ''''''
    tests = list()

    suite_module = importlib.import_module('projects.%s.test_suites.%s' % (project, suite), package=None)
    tests = suite_module.test_case_list

    return tests


def get_test_case_class(project, test):
    '''returns the test case class (located in
        root\\projects\\{project_name}\\test_cases\\{test_case_name.py}'''

    modulex = importlib.import_module('projects.{0}.test_cases.{1}'.format(project, test), package=None)
    return getattr(modulex, test)


def get_parser():
    '''parser of comand line arguments'''
    parser = argparse.ArgumentParser(
        description = 'run a test case, a test suite or start the Golem GUI tool',
        usage = 'golem run project_name test_case|test_suite [-d driver]')

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
        'test',
        metavar='test',
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
    parser.add_argument(
        '-e',
        '--engine',
        metavar='engine',
        default='selenium',
        help='automation engine')

    return parser


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


def run_guiDEPRECATED():
    import webbrowser
    from multiprocessing import Pool

    os.environ["DJANGO_SETTINGS_MODULE"] = "golem.gui.golem-gui.settings"

    from django.core.management import execute_from_command_line

    pool = Pool(processes=1)

    result = pool.apply_async(execute_from_command_line, [['','runserver']])

    webbrowser.open('http://localhost:8000')

    raw_input()
    
def run_gui():
    import webbrowser
    
    # a = os.path.dirname(os.path.abspath(__file__))
    # print a
    # print
    # b = os.path.abspath(os.path.join(a, os.pardir)) + '\\guif\\golem-gui.py'
    # print b
    #os.system(b)

    from golem.gui import app
    app.run(debug=True)
    
    #exec(b)
    
    #import file


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


class _Missing(object):

    def __repr__(self):
        return 'no value'

    def __reduce__(self):
        return '_missing'

_missing = _Missing()
    
class cached_property(object):
    """A decorator that converts a function into a lazy property. The
function wrapped is called the first time to retrieve the result
and then that calculated result is used the next time you access
the value::

class Foo(object):

@cached_property
def foo(self):
# calculate something important here
return 42

The class has to have a `__dict__` in order for this property to
work.
"""

    # implementation detail: this property is implemented as non-data
    # descriptor. non-data descriptors are only invoked if there is
    # no entry with the same name in the instance's __dict__.
    # this allows us to completely get rid of the access function call
    # overhead. If one choses to invoke __get__ by hand the property
    # will still work as expected because the lookup logic is replicated
    # in __get__ for manual invocation.

    def __init__(self, func, name=None, doc=None):
        self.__name__ = name or func.__name__
        self.__module__ = func.__module__
        self.__doc__ = doc or func.__doc__
        self.func = func

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        value = obj.__dict__.get(self.__name__, _missing)
        if value is _missing:
            value = self.func(obj)
            obj.__dict__[self.__name__] = value
        return value
    
    
class lazy_property(object):#deprecated use the above one
    '''
    meant to be used for lazy evaluation of an object attribute.
    property should represent non-mutable data, as it replaces itself.
    '''

    def __init__(self,fget):
        self.fget = fget
        self.func_name = fget.__name__


    def __get__(self,obj,cls):
        if obj is None:
            return None
        value = self.fget(obj)
        setattr(obj,self.func_name,value)
        return value
        

def get_selenium_object(obj, driver):
    if 'id' in obj:
       test_object = driver.find_element_by_id(obj['id'])
    else:
        print 'Object could not be found' #(fix)
    
    return test_object


class Test_context:
    '''used to store all the data related to an execution instance'''

    def __init__(self, 
        root=None,
        project=None, 
        test_case=None, 
        test_suite=None, 
        settings=None, 
        engine=None, 
        selenium_driver=None):

        self.root = root
        self.project = project
        self.test_case = test_case
        self.test_suite = test_suite
        self.settings = settings
        self.engine = engine 
        self.selenium_driver = selenium_driver 
