from golem.core.base_test import Base_test

from golem.core.actions import *

class Testclass(Base_test):

    def run(self, driver, data):
        #setup
        from ..pages import home, article
        home = home.Home()
        article = article.Article(driver)

        driver.get("http://en.wikipedia.org/wiki/Main_Page")

        print 'llegue aca'
        
        a = home.search_button

        print a
        
        click(home.search_button)

        
        #steps
        #home.search_input.send_keys(data['article_name'])
        #home.search_button.click()
        assert article.article_title.text != data['article_name']
        #/steps
