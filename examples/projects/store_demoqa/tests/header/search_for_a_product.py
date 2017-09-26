
description = ''

pages = ['header',
         'checkout',
         'search_result']

def setup(data):
    pass

def test(data):
    navigate('http://store.demoqa.com/')
    send_keys(header.search_input, 'mouse')
    press_key(header.search_input, 'ENTER')
    search_result.verify_product_in_results('Magic Mouse')
    capture('search result')


def teardown(data):
    pass
