
description = ''

pages = ['header',
         'checkout']

def setup(data):
    pass

def test(data):
    navigate('http://store.demoqa.com/')
    click(header.go_to_checkout)
    verify_text_in_element(checkout.title, 'Checkout')
    capture('Checkout page is displayed')


def teardown(data):
    pass
