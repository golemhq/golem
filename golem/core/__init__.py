
import utils

driver = None

#will fail if driver name is not passed and driver not instantiated
def getOrCreateWebdriver(*args):
    global driver
    #driver = driver or utils.get_driver(args[0])

    if not driver:
        if args:
            driver = utils.get_driver(args[0])
            #maximize driver window by default (fix)
            driver.maximize_window()

    return driver
