
description = ''

pages = ['header',
         'checkout']

def setup(data):
    pass

def test(data):
    navigate('http://store.demoqa.com/')
    click(header.go_to_checkout)
    verify_text_in_element(checkout.items_container, 'Oops, there is nothing in your cart.')
    capture('There are no items in the checkout page')


def teardown(data):
    pass
