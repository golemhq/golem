from golem.core.base_test import Base_test

class Testclass(Base_test):

    def run(self, driver, data):
        #setup
        from ..pages import home, article
        home = home.Home(driver)
        article = article.Article(driver)

        driver.get("http://en.wikipedia.org/wiki/Main_Page")

        #steps
        home.search_input.send_keys(data['article_name'])
        home.search_button.click()
        assert article.article_title.text == data['article_name']
        #/steps
