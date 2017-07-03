
description = 'Verify that the application shows the correct error message when creating a project without name'

pages = ['login',
         'index']

def setup(data):
    go_to('http://localhost:8000/')
    login.do_login('admin', 'admin')

def test(data):
    click(index.create_project_button)
    click(index.create_button)
    index.verify_error_message('Project name is too short')


def teardown(data):
    close()
