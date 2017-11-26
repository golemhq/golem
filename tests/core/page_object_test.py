import os
import sys

from golem.core import page_object

from tests.fixtures import testdir_fixture, random_project_fixture
from tests import helper_functions


class Test__get_page_object_content:


    def test_get_page_object_content(self, testdir_fixture, random_project_fixture):

        project = random_project_fixture['name']
        page_name = 'page_test_get_content'

        page_object.new_page_object(testdir_fixture['path'], project, [],
                                    page_name, add_parents=False)
        page_path = os.path.join(testdir_fixture['path'], 'projects',
                                 project, 'pages', page_name + '.py')
        with open(page_path, 'w') as page_file:
            page_file.write('elem1 = (\'id\', \'someId\', \'Elem1\')\n')
            page_file.write('def func1(c, b, a):\n')
            page_file.write('    pass')


        #sys.path.append(testdir_fixture['path'])
        content = page_object.get_page_object_content(project, page_name)

        expected = {
            'function_list': [
                {
                    'function_name': 'func1',
                    'full_function_name': 'page_test_get_content.func1',
                    'description': None,
                    'arguments': ['c', 'b', 'a'],
                    'code': 'def func1(c, b, a):\n    pass\n'
                }],
            'element_list': [
                {
                    'element_name': 'elem1',
                    'element_selector': 'id',
                    'element_value': 'someId',
                    'element_display_name': 'Elem1',
                    'element_full_name': 'page_test_get_content.elem1'
                }],
            'import_lines': [],
            'code_line_list': ["elem1 = ('id', 'someId', 'Elem1')", 'def func1(c, b, a):', '    pass', ''],
            'source_code': "elem1 = ('id', 'someId', 'Elem1')\ndef func1(c, b, a):\n    pass\n"
        }

        assert content == expected

