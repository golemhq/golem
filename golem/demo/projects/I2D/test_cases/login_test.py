#from selenium import webdriver

#import sys

#Login_test():

class Testclass:

    def __init__(self,driver_instance, data):
        driver = driver_instance
        self.run(driver, data)


    def run(self, driver, data):
        #setup

        from ..pages import login

        #steps
        login = login.Login(driver)

        driver.get("http://argenrapp21/Emerios/ES3/RetrieveDocument/login.html")

        #loginPage = Login()
        #print loginPage.__dict__
        #print sys.getsizeof(loginPage)
        #print "t.dict ",loginPage.__dict__
        #print "loginpage.email ", loginPage.email
        #print loginPage.__dict__
        #print loginPage.email

        login.email.send_keys(data['username'])
        #print loginPage.__dict__
        #print sys.getsizeof(loginPage)
        login.password.send_keys(data['password'])
        #print loginPage.__dict__
        #print sys.getsizeof(loginPage)
        login.loginbtn.click()
        #print loginPage.__dict__
        #print sys.getsizeof(loginPage)
        #/steps
