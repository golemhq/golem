
description = 'Verify that the user can create a new page inside a directory'

pages = ['login',
         'index',
         'project']


def setup(data):
    go_to('http://localhost:8000/')
    login.do_login('admin', 'admin')


def test(data):
    index.access_project('test')
    store('dir_name', random('ccccc/'))
    store('page_name', random('ccccc'))
    project.add_new_page(data.dir_name)
    project.add_new_page(data.page_name, data.dir_name)
    project.verify_page_exists(data.page_name, data.dir_name)


def teardown(data):
    close()
