
description = ''

pages = ['header']

def setup(data):
    pass

def test(data):
    navigate('http://store.demoqa.com/')
    click(header.my_account)
    verify_text('You must be logged in to use this page. Please use the form below to login to your account.')


def teardown(data):
    pass
