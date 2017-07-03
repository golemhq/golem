
description = 'Verify that the user cannot log in with in correct password'

pages = ['login']

def setup(data):
    pass

def test(data):
    go_to('http://localhost:8000/')
    send_keys(login.username_input, 'admin')
    send_keys(login.password_input, 'incorect password')
    click(login.login_button)
    capture('Verify the correct error message is shown')
    verify_text_in_element(login.error_list, 'Username and password do not match')


def teardown(data):
    close()
