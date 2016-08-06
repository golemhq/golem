
import selenium_utils

driver = None

#will fail if driver name is not passed and driver not instantiated
def getOrCreateWebdriver(*args):
    global driver
    #driver = driver or utils.get_driver(args[0])

    if not driver:
        driver = selenium_utils.get_driver('firefox')
        #maximize driver window by default (fix)
        driver.maximize_window()

    return driver
