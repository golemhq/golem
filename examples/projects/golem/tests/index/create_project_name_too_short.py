
description = 'Verify that the application shows the correct \
error message when creating a project with the name too short (less than 3 chars long)'

pages = ['login',
         'index']

def setup():
    go_to('http://localhost:8000/')
    login.do_login('admin', 'admin')

def test(data):
    click(index.create_project_button)
    store('project_name', random('c2'))
    send_keys(index.project_name_input, data['project_name'])
    click(index.create_button)
    index.verify_error_message('Project name is too short')


def teardown():
    close()
