
description = 'Verify that the user cannot create a page with a name that contains spaces in the middle'

pages = ['login',
         'index',
         'project']

def setup(data):
    navigate('http://localhost:8000/')
    login.do_login('admin', 'admin')

def test(data):
    index.access_project('test')
    project.add_new_page('test with spaces')
    project.verify_error_message('Spaces are not allowed')


def teardown(data):
    close()
