from golem.selenium import elements


def verify_product_in_results(product_name):
    
    products = elements('.product_grid_display>.product_grid_item')
    for product in products:

        if product.find('.prodtitle>a').text == product_name:
            return
    raise Exception('Product {} was not found'.format(product_name))
