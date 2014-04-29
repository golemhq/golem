from golem.core.base_test import Base_test

class Testclass(Base_test):

    def run(self, driver, data):
        #setup
        from ..pages import home, login
        home = home.Home(driver)
        login = login.Login(driver)

        driver.get("http://en.wikipedia.org/wiki/Main_Page")

        #steps
        home.login_link.click()
        login.username.send_keys('mortecane')
        login.password.send_keys(data['password'])
        #login.login_button.click()
        #assert home.user_link
        #/steps
