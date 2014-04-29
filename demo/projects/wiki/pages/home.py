
class lazy_property(object):
    '''
    meant to be used for lazy evaluation of an object attribute.
    property should represent non-mutable data, as it replaces itself.
    '''

    def __init__(self,fget):
        self.fget = fget
        self.func_name = fget.__name__


    def __get__(self,obj,cls):
        if obj is None:
            return None
        value = self.fget(obj)
        setattr(obj,self.func_name,value)
        return value


class Home(object):

    def __init__(self, driver):
        self.driver = driver

    @lazy_property
    def search_input(self):
        search_input = self.driver.find_element_by_id("searchInput")
        return search_input

    @lazy_property
    def search_button(self):
        search_button = self.driver.find_element_by_id("searchButton")
        return search_button

    @lazy_property
    def login_link(self):
        login_link = self.driver.find_element_by_link_text("Log in")
        return login_link

    @lazy_property
    def user_link(self):
        user_link = self.driver.find_element_by_id("pt-userpage")
        return user_link




