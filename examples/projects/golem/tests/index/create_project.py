
description = 'Verify that the user can create a new project in the index page'

pages = ['login',
         'index']

def setup(data):
    go_to('http://localhost:8000/')
    login.do_login('admin', 'admin')

def test(data):
    click(index.create_project_button)
    store('project_name', random('cccc'))
    wait_for_element_visible(index.project_name_input)
    send_keys(index.project_name_input, data['project_name'])
    click(index.create_button)
    wait_for_element_not_visible(index.create_button)
    index.verify_project_exists(data['project_name'])


def teardown(data):
    close()
