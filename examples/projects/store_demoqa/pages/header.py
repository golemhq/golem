from golem.selenium import get_driver, element
from golem import actions


category_menu = ('id', 'menu-item-33', '')

go_to_checkout = ('css', '#header_cart>a.cart_icon', 'go_to_checkout')

my_account = ('css', '#account>a.account_icon', 'my_account')

search_input = ('css', '.searchform>fieldset>input.search', 'Search input')

def navigate_to_category(category):
    actions.mouse_hover(category_menu)
    menu_categories = element(category_menu).find_all(css='.sub-menu > li > a')
    for m in menu_categories:
        if category in m.get_attribute('innerHTML'):
            m.click()
            return
    raise Exception('Category not found')


def verify_product_categories(categories):
    categories = categories.split(',')
    categories = [x.strip() for x in categories]
    menu_categories = element(category_menu).find_all(css='.sub-menu > li > a')
    menu_categories_text = [x.get_attribute('innerHTML') for x in menu_categories]
    menu_categories_text = [x.replace('<span></span>', '') for x in menu_categories_text]
    categories_missing = []
    for category in categories:
        if category not in menu_categories_text:
            categories_missing.append(category)
    if categories_missing:
        raise Exception('The following categories are missing: {}'
                        .format(','.join(categories_missing)))
