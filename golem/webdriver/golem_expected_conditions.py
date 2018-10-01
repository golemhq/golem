
class element_to_be_enabled(object):
    """An Expectation for checking an element is enabled"""
    def __init__(self, element):
        self.element = element

    def __call__(self, driver):
        return self.element.is_enabled()


class text_to_be_present_in_page(object):
    """An Expectation for checking page contains text"""
    def __init__(self, text):
        self.text = text

    def __call__(self, driver):
        return self.text in driver.page_source


class element_text_to_be(object):
    """An expectation for checking the given text matches element text"""
    def __init__(self, element, text):
        self.element = element
        self.text = text

    def __call__(self, driver):
        return self.element.text == self.text


class element_text_to_contain(object):
    """An expectation for checking element contains the given text"""
    def __init__(self, element, text):
        self.element = element
        self.text = text

    def __call__(self, driver):
        return self.text in self.element.text


class element_to_have_attribute(object):
    """An expectation for checking element has attribute"""
    def __init__(self, element, attribute):
        self.element = element
        self.attribute = attribute

    def __call__(self, driver):
        return self.element.get_attribute(self.attribute) is not None


class window_present_by_partial_title(object):
    """An expectation for checking a window is present by partial title"""
    def __init__(self, partial_title):
        self.partial_title = partial_title

    def __call__(self, driver):
        return any(self.partial_title in t for t in driver.get_window_titles())


class window_present_by_partial_url(object):
    """An expectation for checking a window is present by partial url"""
    def __init__(self, partial_url):
        self.partial_url = partial_url

    def __call__(self, driver):
        return any(self.partial_url in u for u in driver.get_window_urls())


class window_present_by_title(object):
    """An expectation for checking a window is present by title"""
    def __init__(self, title):
        self.title = title

    def __call__(self, driver):
        return self.title in driver.get_window_titles()


class window_present_by_url(object):
    """An expectation for checking a window is present by url"""
    def __init__(self, url):
        self.url = url

    def __call__(self, driver):
        return self.url in driver.get_window_urls()