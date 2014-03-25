from golem.core.base_test import Base_test

class Testclass(Base_test):    

    def run(self, driver, data):
        #setup
        from ..pages import login
        login = login.Login(driver)
        driver.get("http://argenrapp21/Emerios/ES3/RetrieveDocument/login.html")

        #steps
        login.email.send_keys("manager.test@vmbc.com")
        login.password.send_keys("vmbc2013")
        login.loginbtn.click()
        #/steps
