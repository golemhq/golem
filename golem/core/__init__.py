from selenium import webdriver


driver = None

settings = None

project = None


# will fail if driver name is not passed and driver not instantiated
def getOrCreateWebdriver(*args):
    global driver
    # driver = driver or utils.get_driver(args[0])
    driver_selected = 'firefox'
    if not driver:
        # driver = selenium_utils.get_driver('firefox')
        if driver_selected == 'firefox':
            driver = webdriver.Firefox()
        if driver_selected == 'chrome':
            driver = webdriver.Chrome()
        if driver_selected == 'ie':
            driver = webdriver.Ie()
        if driver_selected == 'phantomjs':
            if os.name == 'nt':
                executable_path = os.path.join(
                                            golem.__path__[0],
                                            'lib',
                                            'phantom',
                                            'phantomjs.exe')
                driver = webdriver.PhantomJS(
                                    executable_path=executable_path)
            else:
                print 'not implemented yet'
                sys.exit()
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