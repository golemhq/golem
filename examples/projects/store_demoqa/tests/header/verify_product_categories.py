
description = ''

pages = ['header']

def setup(data):
    pass

def test(data):
    navigate('http://store.demoqa.com/')
    header.verify_product_categories('Accessories, iMacs, iPads, iPhones, iPods, MacBooks')
    capture('Verify product categories')


def teardown(data):
    pass
