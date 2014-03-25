from selenium import webdriver

def lazyprop(fn):
    attr_name = '_lazy_' + fn.__name__
    @property
    def _lazyprop(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)
    return _lazyprop


class LoginPage(object):

    @lazyprop
    def email(self):
		print 'generating "mail"'
		mail = driver.find_element_by_id("email")
		return mail


driver = webdriver.Firefox()
driver.get("http://argenrapp21/Emerios/ES3/RetrieveDocument/login.html")

loginPage = LoginPage()
print "t.dict ",loginPage.__dict__
print "loginpage.email ", loginPage.email
print loginPage.__dict__
print loginPage.email