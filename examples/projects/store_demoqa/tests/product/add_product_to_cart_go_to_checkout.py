
description = ''

pages = ['header', 'category', 'checkout']

def setup(data):
    pass

def test(data):
    navigate('http://store.demoqa.com/')
    header.navigate_to_category('Accessories')
    category.add_product_to_cart('Magic Mouse')
    click(category.go_to_checkout)
    verify_text_in_element(checkout.title, 'Checkout')
    capture('The checkout page is displayed')


def teardown(data):
    pass
