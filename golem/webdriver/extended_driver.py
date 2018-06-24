from typing import List

from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoAlertPresentException, TimeoutException

from golem.webdriver import common
from golem.webdriver.extended_webelement import ExtendedRemoteWebElement
from golem.webdriver import golem_expected_conditions as gec
from golem.core.exceptions import ElementNotFound


class GolemExtendedDriver:

    def accept_alert(self, ignore_not_present=False):
        """Dismiss alert.
        When ignore_not_present is True the error when alert
        is not present is ignored.
        """
        try:
            self.switch_to.alert.accept()
        except NoAlertPresentException:
            if not ignore_not_present:
                raise

    def alert_is_present(self):
        """an alert is present"""
        try:
            self.switch_to.alert
            return True
        except NoAlertPresentException:
            return False

    def check_element(self, element):
        """Check an element (checkbox or radiobutton).
        If element is already checked this is is ignored.
        """
        element = self.find(element)
        element.check()

    def close_window_by_index(self, index):
        """Close window/tab by index.
        Note: "The order in which the window handles are returned is arbitrary."
        """
        if index > len(self.window_handles) - 1:
            raise ValueError('Cannot close window {}, current amount is {}'
                             .format(index, len(self.window_handles)))
        else:
            handle_to_close = self.window_handles[index]
            self.close_window_switch_back(handle_to_close)

    def close_window_by_partial_title(self, partial_title):
        """Close window/tab by partial title"""
        titles = self.get_window_titles()
        title_match = [title for title in titles if partial_title in title]
        if title_match:
            index = titles.index(title_match[0])
            handle_to_close = self.window_handles[index]
            self.close_window_switch_back(handle_to_close)
        else:
            msg = 'a window with partial title \'{}\' was not found'.format(partial_title)
            raise ValueError(msg)

    def close_window_by_partial_url(self, partial_url):
        """Close window/tab by partial url"""
        urls = self.get_window_urls()
        url_match = [url for url in urls if partial_url in url]
        if url_match:
            index = urls.index(url_match[0])
            handle_to_close = self.window_handles[index]
            self.close_window_switch_back(handle_to_close)
        else:
            msg = 'a window with partial URL \'{}\' was not found'.format(partial_url)
            raise ValueError(msg)

    def close_window_by_title(self, title):
        """Close window/tab by title"""
        titles = self.get_window_titles()
        if title in titles:
            handle_to_close = self.window_handles[titles.index(title)]
            self.close_window_switch_back(handle_to_close)
        else:
            raise ValueError('a window with title \'{}\' was not found'.format(title))

    def close_window_by_url(self, url):
        """Close window/tab by URL"""
        urls = self.get_window_urls()
        if url in urls:
            handle_to_close = self.window_handles[urls.index(url)]
            self.close_window_switch_back(handle_to_close)
        else:
            raise ValueError('a window with URL \'{}\' was not found'.format(url))

    def close_window_switch_back(self, close_handle):
        """Close a window/tab by handle and switch back to current handle.
        If current handle is the same as close_handle, try to switch to the
        first available window/tab.
        """
        current_handle = self.current_window_handle
        self.switch_to.window(close_handle)
        self.close()
        if current_handle == close_handle:
            # closing active window, try to switch
            # to first window
            if self.window_handles:
                self.switch_to_first_window()
        else:
            # closing another window.
            # switch back to original handle
            self.switch_to.window(current_handle)

    def dismiss_alert(self, ignore_not_present=False):
        """Dismiss alert.
        When ignore_not_present is True the error when alert
        is not present is ignored.
        """
        try:
            self.switch_to.alert.dismiss()
        except NoAlertPresentException:
            if not ignore_not_present:
                raise

    def element_is_present(self, element):
        """If element is present, return the element.
        If element is not present return False
        """
        try:
            element = self.find(element, timeout=0)
            return element
        except ElementNotFound:
            return False

    # def drag_and_drop(self, element, target):
    #     actionChains = ActionChains(self)
    #     source_element = self.find(element)
    #     target_element = self.find(target)
    #     actionChains.drag_and_drop(source_element, target_element).perform()

    def find(self, *args, **kwargs) -> ExtendedRemoteWebElement:
        if len(args) == 1:
            kwargs['element'] = args[0]
        return common._find(self, **kwargs)

    def find_all(self, *args, **kwargs) -> List[ExtendedRemoteWebElement]:
        if len(args) == 1:
            kwargs['element'] = args[0]
        return common._find_all(self, **kwargs)

    def get_window_index(self):
        """Get the index of the current window/tab"""
        return self.window_handles.index(self.current_window_handle)

    def get_window_titles(self):
        """Return a list of the titles of all open windows/tabs"""
        original_handle = self.current_window_handle
        titles = []
        for handle in self.window_handles:
            self.switch_to.window(handle)
            titles.append(self.title)
        self.switch_to.window(original_handle)
        return titles

    def get_window_urls(self):
        """Return a list of the URLs of all open windows/tabs"""
        original_handle = self.current_window_handle
        urls = []
        for handle in self.window_handles:
            self.switch_to.window(handle)
            urls.append(self.current_url)
        self.switch_to.window(original_handle)
        return urls

    def navigate(self, url):
        self.get(url)

    def switch_to_first_window(self):
        """Switch to last window/tab"""
        self.switch_to_window_by_index(0)

    def switch_to_last_window(self):
        """Switch to window/tab by index"""
        self.switch_to.window(self.window_handles[-1])

    def switch_to_next_window(self):
        """Switch to next window/tab in the list of window handles.
        If current window is the last in the list this will circle
        back from the start.
        """
        next_index = self.get_window_index() + 1
        if next_index < len(self.window_handles):
            self.switch_to_window_by_index(next_index)
        else:
            self.switch_to_window_by_index(0)

    def switch_to_previous_window(self):
        """Switch to previous window/tab in the list of window handles.
        If current window is the first in the list this will circle
        back from the top.
        """
        previous_index = self.get_window_index() -1
        if previous_index >= 0:
            self.switch_to_window_by_index(previous_index)
        else:
            self.switch_to_window_by_index(len(self.window_handles) -1)

    def switch_to_window_by_index(self, index):
        """Switch to window/tab by index.
        Note: "The order in which the window handles are returned is arbitrary."
        """
        self.switch_to.window(self.window_handles[index])

    def switch_to_window_by_partial_title(self, partial_title):
        """Switch to window/tab by partial title"""
        for handle in self.window_handles:
            self.switch_to.window(handle)
            if partial_title in self.title:
                return
        raise Exception('Window with partial title \'{}\' was not found'.format(partial_title))

    def switch_to_window_by_partial_url(self, partial_url):
        """Switch to window/tab by partial URL"""
        for handle in self.window_handles:
            self.switch_to.window(handle)
            if partial_url in self.current_url:
                return
        raise Exception('Window with partial URL \'{}\' was not found'.format(partial_url))

    def switch_to_window_by_title(self, title):
        """Switch to window/tab by title"""
        for handle in self.window_handles:
            self.switch_to.window(handle)
            if self.title == title:
                return
        raise Exception('Window with title \'{}\' was not found'.format(title))

    def switch_to_window_by_url(self, url):
        """Switch to window/tab by URL"""
        for handle in self.window_handles:
            self.switch_to.window(handle)
            if self.current_url == url:
                return
        raise Exception('Window with URL \'{}\' was not found'.format(url))

    def uncheck_element(self, element):
        """Uncheck a checkbox element.
        If element is already unchecked this is is ignored.
        """
        element = self.find(element)
        element.uncheck()

    def wait_for_alert_present(self, timeout):
        """Wait for an alert to be present"""
        wait = WebDriverWait(self, timeout)
        message = 'Timeout waiting for alert to be present'
        wait.until(ec.alert_is_present(), message=message)

    def wait_for_element_displayed(self, element, timeout):
        """Wait for element to be present and displayed"""
        element = self.find(element, timeout=timeout, wait_displayed=True)
        if element and not element.is_displayed():
            message = ('Timeout waiting for element {} to be displayed'
                       .format(self.name))
            raise TimeoutException(message)

    def wait_for_element_enabled(self, element, timeout):
        """Wait for element to be enabled"""
        element = self.find(element, timeout=0)
        return element.wait_enabled(timeout)

    def wait_for_element_has_attribute(self, element, attribute, timeout):
        """Wait for element to have attribute"""
        element = self.find(element, timeout=0)
        return element.wait_has_attribute(attribute, timeout)

    def wait_for_element_has_not_attribute(self, element, attribute, timeout):
        """Wait for element to not have attribute"""
        element = self.find(element, timeout=0)
        return element.wait_has_not_attribute(attribute, timeout)

    def wait_for_element_not_displayed(self, element, timeout):
        """Wait for element to be not displayed"""
        element = self.find(element, timeout=0)
        return element.wait_not_displayed(timeout)

    def wait_for_element_not_enabled(self, element, timeout):
        """Wait for element to be not enabled"""
        element = self.find(element, timeout=0)
        return element.wait_not_enabled(timeout)

    def wait_for_element_not_present(self, element, timeout):
        """Wait for element present in the DOM"""
        found_element = None
        try:
            found_element = self.find(element, timeout=0)
        except ElementNotFound:
            pass
        if found_element:
            wait = WebDriverWait(self, timeout)
            message = ('Timeout waiting for element {} to not be present'
                       .format(found_element.name))
            wait.until(ec.staleness_of(found_element), message=message)

    def wait_for_element_present(self, element, timeout):
        """Wait for element present in the DOM"""
        self.find(element, timeout=timeout, wait_displayed=False)

    def wait_for_element_text(self, element, text, timeout):
        """Wait for element text to match given text"""
        element = self.find(element, timeout=0)
        return element.wait_text(text, timeout)

    def wait_for_element_text_contains(self, element, text, timeout):
        """Wait for element to contain text"""
        element = self.find(element, timeout=0)
        return element.wait_text_contains(text, timeout)

    def wait_for_element_text_is_not(self, element, text, timeout):
        """Wait for element text to not match given text"""
        element = self.find(element, timeout=0)
        return element.wait_text_is_not(text, timeout)

    def wait_for_element_text_not_contains(self, element, text, timeout):
        """Wait for element to not contain text"""
        element = self.find(element, timeout=0)
        return element.wait_text_not_contains(text, timeout)

    def wait_for_page_contains_text(self, text, timeout):
        """Wait for page to contains text"""
        wait = WebDriverWait(self, timeout)
        message = "Timeout waiting for page to contain '{}'".format(text)
        wait.until(gec.text_to_be_present_in_page(text), message=message)

    def wait_for_page_not_contains_text(self, text, timeout):
        """Wait for page to not contain text"""
        wait = WebDriverWait(self, timeout)
        message = "Timeout waiting for page to not contain '{}'".format(text)
        wait.until_not(gec.text_to_be_present_in_page(text), message=message)

    def wait_for_title(self, title, timeout):
        """Wait for page title to be the given value"""
        wait = WebDriverWait(self, timeout)
        message = 'Timeout waiting for title to be \'{}\''.format(title)
        wait.until(ec.title_is(title), message=message)

    def wait_for_title_contains(self, partial_title, timeout):
        """Wait for page title to contain partial_title"""
        wait = WebDriverWait(self, timeout)
        message = 'Timeout waiting for title to contain \'{}\''.format(partial_title)
        wait.until(ec.title_contains(partial_title), message=message)

    def wait_for_title_is_not(self, title, timeout):
        """Wait for page title to not be the given value"""
        wait = WebDriverWait(self, timeout)
        message = 'Timeout waiting for title to not be \'{}\''.format(title)
        wait.until_not(ec.title_is(title), message=message)

    def wait_for_title_not_contains(self, partial_title, timeout):
        """Wait for page title to not contain partial_title"""
        wait = WebDriverWait(self, timeout)
        message = 'Timeout waiting for title to not contain \'{}\''.format(partial_title)
        wait.until_not(ec.title_contains(partial_title), message=message)

    def wait_for_window_present_by_partial_title(self, partial_title, timeout):
        """Wait for window/tab present by partial title"""
        wait = WebDriverWait(self, timeout)
        message = 'Timeout waiting for window present by partial title \'{}\''.format(partial_title)
        wait.until(gec.window_present_by_partial_title(partial_title), message=message)

    def wait_for_window_present_by_partial_url(self, partial_url, timeout):
        """Wait for window/tab present by partial url"""
        wait = WebDriverWait(self, timeout)
        message = 'Timeout waiting for window present by partial url \'{}\''.format(partial_url)
        wait.until(gec.window_present_by_partial_url(partial_url), message=message)

    def wait_for_window_present_by_title(self, title, timeout):
        """Wait for window/tab present by title"""
        wait = WebDriverWait(self, timeout)
        message = 'Timeout waiting for window present by title \'{}\''.format(title)
        wait.until(gec.window_present_by_title(title), message=message)

    def wait_for_window_present_by_url(self, url, timeout):
        """Wait for window/tab present by url"""
        wait = WebDriverWait(self, timeout)
        message = 'Timeout waiting for window present by url \'{}\''.format(url)
        wait.until(gec.window_present_by_url(url), message=message)