#from selenium import webdriver
#import base

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


class Article(object):

    def __init__(self, driver):
        self.driver = driver

    @lazy_property
    def article_title(self):
        article_title = self.driver.find_element_by_id("firstHeading")
        return article_title

    @lazy_property
    def loginbtn(self):
        loginbtn = self.driver.find_element_by_id("login")
        return loginbtn

    def do_login(self, email, password):
        self.email.send_keys(email)
