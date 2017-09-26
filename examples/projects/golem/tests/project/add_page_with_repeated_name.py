
description = 'Verify that the application displays the correct error message when the page name already exists'

pages = ['login',
         'index',
         'project']


def setup(data):
    go_to('http://localhost:8000/')
    login.do_login('admin', 'admin')


def test(data):
    index.access_project('test')
    store('page_name', random('ccccc'))
    project.add_new_page(data.page_name)
    project.add_new_page(data.page_name)
    project.verify_error_message('A file with that name already exists')


def teardown(data):
    close()
