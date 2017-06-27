
description = 'Verify that the user can create a new project in the index page'

pages = ['login',
         'index']

def setup():
    go_to('http://localhost:8000/')
    login.do_login('admin', 'admin')

def test(data):
    click(index.create_project_button)
    store('project_name', random('c5'))
    send_keys(index.project_name_input, data['project_name'])
    click(index.create_button)
    capture('verify the project exists in the list')
    index.verify_project_exists(data['project_name'])


def teardown():
    close()
