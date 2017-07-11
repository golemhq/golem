
description = 'Verify that the user can create a new page from the project page'

pages = ['login',
         'index',
         'project']

def setup(data):
    go_to('http://localhost:8000/')
    login.do_login('admin', 'admin')

def test(data):
    index.access_project('test')
    store('page_name', random('ccccc'))
    project.add_new_page(data['page_name'])
    project.verify_page_exists(data['page_name'])


def teardown(data):
    close()
