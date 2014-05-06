from golem.core.utils import cached_property, _missing



class Home(object):

    def __init__(self, driver):
        self.driver = driver

    @cached_property
    def search_input(self):
        search_input = self.driver.find_element_by_id("searchInput")
        return search_input

    @cached_property
    def search_button(self):
        search_button = self.driver.find_element_by_id("searchButton")
        return search_button

    @cached_property
    def login_link(self):
        login_link = self.driver.find_element_by_link_text("Log in")
        return login_link

    @cached_property
    def user_link(self):
        user_link = self.driver.find_element_by_id("pt-userpage")
        return user_link




