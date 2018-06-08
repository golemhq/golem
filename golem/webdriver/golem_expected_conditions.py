
class element_to_be_enabled(object):
    """An Expectation for checking an element is enabled"""
    def __init__(self, element):
        self.element = element

    def __call__(self, driver):
        return self.element.is_enabled()