from selenium import webdriver


driver = None

settings = None

project = None

workspace = None


# will fail if driver name is not passed and driver not instantiated
def getOrCreateWebdriver(*args):
    global settings
    global driver

    if not driver:

        if settings['driver']:
            driver_selected = settings['driver']
        elif 'default_driver' in settings:
            driver_selected = settings['default_driver']
        else:
            driver_selected = 'firefox'

        if driver_selected == 'firefox':
            driver = webdriver.Firefox()
        if driver_selected == 'chrome':
            driver = webdriver.Chrome(executable_path=settings['chrome_driver_path'])
        # if driver_selected == 'ie':
        #     driver = webdriver.Ie()
        # if driver_selected == 'phantomjs':
        #     if os.name == 'nt':
        #         executable_path = os.path.join(
        #                                     golem.__path__[0],
        #                                     'lib',
        #                                     'phantom',
        #                                     'phantomjs.exe')
        #         driver = webdriver.PhantomJS(
        #                             executable_path=executable_path)
            # else:
            #     print('not implemented yet')
            #     sys.exit()
        # maximize driver window by default (fix)
        driver.maximize_window()

    return driver


def reset_driver_object():
    global driver 
    driver = None


def set_settings(settings_):
    global settings
    settings = settings_


def get_setting(setting):
    if setting in settings:
        return settings[setting]
    else:
        return False