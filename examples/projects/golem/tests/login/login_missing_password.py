
description = 'Verify that the user cannot log in if password value is missing'

pages = ['login']

def setup(data):
    pass

def test(data):
    go_to('http://localhost:8000/')
    send_keys(login.username_input, 'admin')
    click(login.login_button)
    capture('Verify the correct error message is shown')
    verify_text_in_element(login.error_list, 'Password is required')


def teardown(data):
    close()
