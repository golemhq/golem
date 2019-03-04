import os

from golem.core import page_object


class TestPageExists:

    def test_page_exists(self, project_session):
        testdir, project = project_session.values()
        page_object.new_page_object(testdir, project, [], 'page_x001_exist')
        exists = page_object.page_exists(testdir, project, 'page_x001_exist')
        not_exists = page_object.page_exists(testdir, project, 'page_x001_not_exist')
        assert exists
        assert not not_exists


class TestGetPageObjectContent:

    def test_get_page_object_content(self, project_session):
        testdir = project_session.testdir
        project = project_session.name
        page_name = 'page_test_get_content_ab1412'
        page_object.new_page_object(testdir, project, [], page_name)
        page_path = os.path.join(project_session.path, 'pages', page_name + '.py')
        with open(page_path, 'w') as page_file:
            page_file.write('elem1 = (\'id\', \'someId\', \'Elem1\')\n')
            page_file.write('def func1(c, b, a):\n')
            page_file.write('    pass')
        from golem.core import test_execution
        test_execution.root_path = testdir
        content = page_object.get_page_object_content(project, page_name)
        expected = {
            'functions': [
                {
                    'function_name': 'func1',
                    'full_function_name': 'page_test_get_content_ab1412.func1',
                    'description': None,
                    'arguments': ['c', 'b', 'a'],
                    'code': 'def func1(c, b, a):\n    pass\n'
                }],
            'elements': [
                {
                    'element_name': 'elem1',
                    'element_selector': 'id',
                    'element_value': 'someId',
                    'element_display_name': 'Elem1',
                    'element_full_name': 'page_test_get_content_ab1412.elem1'
                }],
            'import_lines': [],
            'code_lines': ["elem1 = ('id', 'someId', 'Elem1')",
                           'def func1(c, b, a):',
                           '    pass',
                           ''],
            'source_code': ("elem1 = ('id', 'someId', 'Elem1')\ndef func1(c, b, a):\n"
                            "    pass\n")
        }
        assert content == expected


class TestGetPageObjectCode:

    def test_get_page_object_code(self, project_session):
        testdir = project_session.testdir
        project = project_session.name
        page_name = 'page_test_get_code_ab8456'

        page_object.new_page_object(testdir, project, [], page_name)
        page_path = os.path.join(project_session.path, 'pages', page_name + '.py')
        file_content = 'test=("id", "xyz")\ntest2=("id", "abc")\n'
        with open(page_path, 'w') as page_file:
            page_file.write(file_content)
        code = page_object.get_page_object_code(page_path)
        assert code == file_content

    def test_get_page_object_code_file_not_exist(self, project_session):
        page_path = os.path.join(project_session.path, 'pages', 'does', 'not', 'exist54654.py')
        code = page_object.get_page_object_code(page_path)
        assert code == ''


class TestSavePageObject:

    def test_save_page_object(self, project_session):
        testdir = project_session.testdir
        project = project_session.name
        page_path = os.path.join(project_session.path, 'pages', 'testa', 'testb', 'page_test987.py')
        page_object.new_page_object(testdir, project, ['testa', 'testb'], 'page_test987')
        page_name = 'testa.testb.page_test987'
        elements = [
            {'name': 'a', 'selector': 'id', 'value': 'b', 'display_name': 'a'},
            {'name': 'c', 'selector': 'id', 'value': 'd', 'display_name': ''}
        ]
        functions = ["def func1(a, b):\n    print(a, b)\n"]
        import_lines = [
            'import time',
            'from golem import browser'
        ]
        page_object.save_page_object(testdir, project, page_name,
                                     elements, functions, import_lines)
        expected_contents = ('import time\n'
                             'from golem import browser\n'
                             '\n'
                             '\n'
                             'a = (\'id\', \'b\', \'a\')\n'
                             '\n'
                             'c = (\'id\', \'d\', \'c\')\n'
                             '\n'
                             'def func1(a, b):\n'
                             '    print(a, b)\n')
        with open(page_path) as page_file:
            contents = page_file.read()
            assert contents == expected_contents


class TestSavePageObjectCode:

    def test_save_page_object_code(self, project_session):
        testdir = project_session.testdir
        project = project_session.name
        page_name = 'page_name_x1'
        parents = ['save', 'page', 'code']
        page_object.new_page_object(testdir, project, parents, page_name)

        page_code = ("elem1 = ('id', 'x')\n"
                     "elem2 = ('id', 'y')\n"
                     "def func1():\n"
                     "   pass")
        full_page_name = '{}.{}'.format('.'.join(parents), page_name)
        page_object.save_page_object_code(testdir, project, full_page_name, page_code)
        full_path = os.path.join(project_session.path, 'pages',
                                 os.sep.join(parents), page_name + '.py')
        with open(full_path) as page_file:
            content = page_file.read()
            assert content == page_code


class TestNewPageObject:

    def test_new_page_object(self, project_session):
        testdir = project_session.testdir
        project = project_session.name
        page_name = 'page_name_x2'
        parents = ['new', 'page', 'object']
        page_object.new_page_object(testdir, project, parents, page_name)
        full_path = os.path.join(project_session.path, 'pages',
                                 os.sep.join(parents), page_name + '.py')
        assert os.path.isfile(full_path)

    def test_new_page_object_page_exists(self, project_session):
        testdir = project_session.testdir
        project = project_session.name
        page_name = 'page_name_x3'
        parents = ['new', 'page', 'object']
        page_object.new_page_object(testdir, project, parents, page_name)
        error = page_object.new_page_object(testdir, project, parents, page_name)
        assert error == ['A page file with that name already exists']

    def test_new_page_object_into_subdirectory(self, project_session):
        testdir = project_session.testdir
        project = project_session.name
        page_name = 'page_name_x3'
        parents = ['subdir']
        page_object.new_page_object(testdir, project, parents, page_name)
        init_path = os.path.join(project_session.path, 'pages', 'subdir', '__init__.py')
        assert os.path.isfile(init_path)


class TestGeneratePagePath:

    def test_generate_page_path(self):
        testdir = 'x'
        project = 'y'
        full_page_name = 'a.b.c'
        expected = os.path.join(testdir, 'projects', project, 'pages', 'a', 'b', 'c.py')
        actual = page_object.generate_page_path(testdir, project, full_page_name)
        assert actual == expected


class TestPageBaseDir:

    def test_pages_base_dir(self):
        testdir = 'x'
        project = 'y'
        expected = os.path.join(testdir, 'projects', project, 'pages')
        actual = page_object.pages_base_dir(testdir, project)
        assert actual == expected
