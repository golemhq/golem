
description = ''

pages = ['header',
         'category']

def setup(data):
    pass

def test(data):
    navigate('http://store.demoqa.com/')
    header.navigate_to_category('Accessories')
    click(category.add_to_cart_button)
    #wait_for_element_visible(category.you_just_added_modal, '10')
    #verify_is_visible(category.you_just_added_modal)
    capture('You just added product modal is displayed')


def teardown(data):
    pass
