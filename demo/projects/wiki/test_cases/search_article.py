from golem.core.base_test import Base_test

from golem.core.actions import *

class search_article(Base_test):	
	
	
    def run(self):
        #setup
        from ..pages import *		
		home = home.Home()
        article = article.Article()
		
		#test
		goto("http://en.wikipedia.org/wiki/Main_Page")        
        click(home.search_button)
        #home.search_input.send_keys(data['article_name']) 		
        assert article.article_title.text != data['article_name']
		
		#tear down
		
		
		close()