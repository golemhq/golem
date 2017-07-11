from golem.core import actions
from golem.selenium.utils import element, elements


new_page_button = ('css', "#pagesTree .display-new-element-link a", 'new_page_button')

new_page_input = ('css', '#pagesTree .new-element-form', 'new_pages_input')


def click_pages_add_new(path=''):
    split_path = []
    if len(path):
        split_path = path.split('.')
    selector = '#pagesTree >'
    for i in range(len(split_path)):
        branch = split_path[i]
        this_branch_selector += 'li[data-branch-name=\'{}\'] > a'.format(branch)
        element(css=this_branch_selector).click()
        selector = selector +'li[data-branch-name=\'{}\'] ul '.format(branch)
    selector += ' li > span > a'
    element(css=selector).click()


def add_new_page(name, path=''):
    split_path = []
    if len(path):
        split_path = path.split('.')
    selector = '#pagesTree >'
    for i in range(len(split_path)):
        branch = split_path[i]
        this_branch_selector += 'li[data-branch-name=\'{}\'] > a'.format(branch)
        element(css=this_branch_selector).click()
        selector = selector +'li[data-branch-name=\'{}\'] ul '.format(branch)
    add_link_selector = selector + ' li > span > a'
    element(css=add_link_selector).click()
    add_input_selector = selector + 'li > span > input.new-element-input'
    add_page_input = ('css', add_input_selector, 'add input')
    actions.send_keys(add_page_input, name)
    actions.press_key(add_page_input, 'ENTER')


def verify_page_exists(full_path):
    split_path = []
    if len(full_path):
        split_path = full_path.split('.')
    dir_name = split_path.pop()
    selector = 'ul#pagesTree >'
    for i in range(len(split_path)):
        branch = split_path[i]
        this_branch_selector += 'li[data-branch-name=\'{}\'] > a'.format(branch)
        element(css=this_branch_selector).click()
        selector = selector +'li[data-branch-name=\'{}\'] ul '.format(branch)

    list_of_lis_selector = selector + ' li.tree-element'
    list_of_lis = elements(css=list_of_lis_selector)
    if not dir_name in [x.text for x in list_of_lis]:
        raise Exception('Page {} was not found'.format(dir_name))
