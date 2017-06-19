from golem.core import actions


username_input = ('id', "username", 'username')

password_input = ('id', "password", 'password')

login_button = ('css', "button[type='submit']", 'login_button')

error_list = ('id', 'errorList', 'Error list')


def do_login(username, password):
    actions.send_keys(username_input, username)
    actions.send_keys(password_input, password)
    actions.click(login_button)