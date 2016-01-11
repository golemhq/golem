from golem.core.test import Test
#page objects
from project1.pages import page1, module1.page2

class Test_case1(Test):

    description = '''this is the 
    description'''
    
    def setup(self):
        pass

    def test(self):
        click(page1.element1)
        send_keys(page1.element1, 'lalala', 'lololo')

    def teardown(self):
        close()