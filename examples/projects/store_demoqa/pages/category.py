from golem.selenium import get_driver, element, elements
from golem import actions


add_to_cart_button = ('css', 'input.wpsc_buy_button', 'add_to_cart_button')

you_just_added_modal = ('id', 'fancy_notification', 'you_just_added_modal')

go_to_checkout = ('css', 'a.go_to_checkout', 'Go To Checkout button')

def add_product_to_cart(product_name):

    products = elements('div.default_product_display')
    for product in products:
        if product.find('.prodtitle>a.wpsc_product_title').text == product_name:
            button = product.find(add_to_cart_button)
            actions.click(button)
            return
    raise Exception('The product with name {} was not found'.format(product_name))