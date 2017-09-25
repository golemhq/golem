
description = 'Verify that the user can add a directory in the pages section by appending \'\\\' at the end'

pages = ['login',
         'index',
         'project']


def setup(data):
    go_to('http://localhost:8000/')
    login.do_login('admin', 'admin')


def test(data):
    index.access_project('test')
    store('directory_name', random('ccccc/'))
    project.add_new_page(data.directory_name)
    project.verify_page_exists(data.directory_name)


def teardown(data):
    close()
