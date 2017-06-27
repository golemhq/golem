
description = 'Verify that the user can create a new page from the project page'

pages = ['login',
         'index',
         'project']

def setup():
    go_to('http://localhost:8000/')
    login.do_login('admin', 'admin')

def test(data):
    index.access_project('test')
    project.add_new_page('page1')
    wait(3)


def teardown():
    close()
