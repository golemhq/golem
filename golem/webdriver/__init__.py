from selenium.webdriver import Chrome as SeleniumChromeDriver
from selenium.webdriver import Edge as SeleniumEdgeDriver
from selenium.webdriver import Firefox as SeleniumGeckoDriver
from selenium.webdriver import Ie as SeleniumIeDriver
from selenium.webdriver import Opera as SeleniumOperaDriver
from selenium.webdriver import Remote as SeleniumRemoteDriver

from golem.webdriver.extended_driver import GolemExtendedDriver


class GolemChromeDriver(SeleniumChromeDriver, GolemExtendedDriver):
    pass


class GolemEdgeDriver(SeleniumEdgeDriver, GolemExtendedDriver):
    pass


class GolemGeckoDriver(SeleniumGeckoDriver, GolemExtendedDriver):
    pass


class GolemIeDriver(SeleniumIeDriver, GolemExtendedDriver):
    pass


class GolemOperaDriver(SeleniumOperaDriver, GolemExtendedDriver):
    pass


class GolemRemoteDriver(SeleniumRemoteDriver, GolemExtendedDriver):
    pass
