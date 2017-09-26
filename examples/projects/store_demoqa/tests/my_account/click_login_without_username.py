
description = ''

pages = ['header',
         'my_account']

def setup(data):
    pass

def test(data):
    navigate('http://store.demoqa.com/')
    click(header.my_account)
    send_keys(my_account.password, 'some_password')
    click(my_account.login_button)
    wait_for_element_not_visible(my_account.loading_icon)
    wait_for_element_visible(my_account.error_message)
    verify_text_in_element(my_account.error_message, 'ERROR: The username field is empty.')
    capture('Error message')


def teardown(data):
    pass
