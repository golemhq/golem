
description = 'Verify that the application shows the correct error message when the user tries to create a project with non unique name'

pages = ['login',
         'index']

def setup(data):
    go_to('http://localhost:8000/')
    login.do_login('admin', 'admin')

def test(data):
    click(index.create_project_button)
    store('project_name', random('ccccc'))
    send_keys(index.project_name_input, data['project_name'])
    click(index.create_button)
    click(index.create_project_button)
    send_keys(index.project_name_input, data['project_name'])
    click(index.create_button)
    index.verify_error_message('A project with that name already exists')


def teardown(data):
    close()
