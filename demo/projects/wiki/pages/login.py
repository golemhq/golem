
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


class Login(object):

    def __init__(self, driver):
        self.driver = driver

    @lazy_property
    def username(self):
        username = self.driver.find_element_by_id("wpName1")
        return username

    @lazy_property
    def password(self):
        password = self.driver.find_element_by_id("wpPassword1")
        return password


    @lazy_property
    def login_button(self):
        login_button = self.driver.find_element_by_id("wpLoginAttempt")
        return login_button

    @lazy_property
    def error_message(self):
        error_message = self.driver.find_element_by_class_name("errorbox")
        return error_message








