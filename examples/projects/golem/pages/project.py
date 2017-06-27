from golem.core import actions, getOrCreateWebdriver


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
        actions.click(('css', this_branch_selector, 'branch'))
        selector = selector +'li[data-branch-name=\'{}\'] ul '.format(branch)
    selector += ' li > span > a'
    actions.click(('css', selector, 'branch'))


def add_new_page(name, path=''):
    split_path = []
    if len(path):
        split_path = path.split('.')
    selector = '#pagesTree >'
    for i in range(len(split_path)):
        branch = split_path[i]
        this_branch_selector += 'li[data-branch-name=\'{}\'] > a'.format(branch)
        actions.click(('css', this_branch_selector, 'branch'))
        selector = selector +'li[data-branch-name=\'{}\'] ul '.format(branch)
    add_link_selector = selector + ' li > span > a'
    actions.click(('css', selector, 'branch'))
    add_input_selector = add_link_selector + 'li > span > input.new-element-input'
    actions.send_keys(('css', add_input_selector, 'add input'))



    