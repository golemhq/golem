#import sys
#import os
#import types

#from selenium import webdriver
#from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
#from selenium.common.exceptions import WebDriverException

#from golem.core import execution_logger as logger
#from golem.selenium import _find, _find_all
#from golem import execution


# def get_or_create_webdriver():
#     driver = execution.driver
#     if not driver:
#         driver = None
#         driver_name = execution.driver_name
#         settings = execution.settings
#         if driver_name == 'firefox':
#             if settings['gecko_driver_path']:
#                 try:
#                     driver = webdriver.Firefox(executable_path=settings['gecko_driver_path'])
#                 except:
#                     msg = ('Could not start firefox driver using the path \'{}\', '
#                            'check the settings file.'.format(settings['gecko_driver_path']))
#                     logger.logger.error(msg)
#                     raise Exception(msg) from None
#             else:
#                 raise Exception('gecko_driver_path setting is not defined')
#         elif driver_name == 'chrome':
#             if settings['chrome_driver_path']:
#                 try:
#                     driver = webdriver.Chrome(executable_path=settings['chrome_driver_path'])
#                 except:
#                     msg = ('Could not start chrome driver using the path \'{}\', '
#                            'check the settings file.'.format(settings['chrome_driver_path']))
#                     logger.logger.error(msg)
#                     raise Exception(msg) from None
#             else:
#                 raise Exception('chrome_driver_path setting is not defined')
#         elif driver_name == 'chrome-headless':
#             if settings['chrome_driver_path']:
#                 try:
#                     options = webdriver.ChromeOptions()
#                     options.add_argument('headless')
#                     options.add_argument('--window-size=1600,1600')
#                     driver = webdriver.Chrome(executable_path=settings['chrome_driver_path'],
#                                               chrome_options=options)
#                 except:
#                     msg = ('Could not start chrome driver using the path \'{}\', '
#                            'check the settings file.'.format(settings['chrome_driver_path']))
#                     logger.logger.error(msg)
#                     raise Exception(msg) from None
#             else:
#                 raise Exception('chrome_driver_path setting is not defined')
#         # if driver_selected == 'ie':
#         #     driver = webdriver.Ie()
#         # if driver_selected == 'phantomjs':
#         #     if os.name == 'nt':
#         #         executable_path = os.path.join(
#         #                                     golem.__path__[0],
#         #                                     'lib',
#         #                                     'phantom',
#         #                                     'phantomjs.exe')
#         #         driver = webdriver.PhantomJS(
#         #                             executable_path=executable_path)
#             # else:
#             #     print('not implemented yet')
#             #     sys.exit()
#         # maximize driver window by default (fix)
#         elif driver_name == 'chrome-remote-headless':
#             options = webdriver.ChromeOptions()
#             options.add_argument('headless')
#             os.environ["webdriver.chrome.driver"] = settings['chrome_driver_path']
#             desired_capabilities = options.to_capabilities()
#             driver = webdriver.Remote(command_executor=settings['remote_url'],
#                                       desired_capabilities=desired_capabilities)
#         elif driver_name == 'chrome-remote':
#             driver = webdriver.Remote(command_executor=settings['remote_url'],
#                                       desired_capabilities=DesiredCapabilities.CHROME)
#         elif driver_name == 'firefox-remote':
#             driver = webdriver.Remote(command_executor=settings['remote_url'],
#                                       desired_capabilities=DesiredCapabilities.FIREFOX)
#         else:
#             raise Exception('Error: {} is not a valid driver'.format(driver_name))

#         driver.maximize_window()

#     execution.driver = driver

#     # bind _find method to driver instance
#     driver.find = types.MethodType(_find, driver)
#     driver.find_all = types.MethodType(_find_all, driver)

#     return execution.driver
