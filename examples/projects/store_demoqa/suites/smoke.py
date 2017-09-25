

browsers = [
    'chrome-headless'
]

workers = 2

tests = [
    'checkout.*',
    'header.verify_product_categories',
    'my_account.login_with_invalid_credentials',
    'product.add_product_to_cart_go_to_checkout'
]
