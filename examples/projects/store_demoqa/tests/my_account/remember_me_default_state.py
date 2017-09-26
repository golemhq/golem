
description = ''

pages = ['header',
         'my_account']

def setup(data):
    pass

def test(data):
    navigate('http://store.demoqa.com/')
    click(header.my_account)
    verify_is_not_selected(my_account.remember_me)
    capture('Remember me is not selected')


def teardown(data):
    pass
