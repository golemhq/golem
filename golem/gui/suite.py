import importlib
import os
import types
import inspect

from golem.core import utils

from golem.gui import gui_utils



# def get_page_object_content(root_path, project, full_po_name):
#     po, parents = utils.separate_file_from_parents(full_po_name)

#     modulex = importlib.import_module('projects.{0}.pages.{1}'
#                                       .format(project, full_po_name))
#     variable_list = [item for item in dir(modulex) if not item.startswith("__")]
#     element_list = []
#     function_list = []
#     import_lines = []
#     # get all the import lines in a list
#     source_code_list = []
#     try:
#         source_code_list = inspect.getsource(modulex).split('\n')
#     except:
#         pass
#     for line in source_code_list:
#         if 'import' in line:
#             import_lines.append(line)
#     for var_name in variable_list:
#         variable = getattr(modulex, var_name)
#         if isinstance(variable, types.FunctionType):
#             # this is a function
#             new_function = {
#                 'function_name': var_name,
#                 'full_function_name': ''.join([full_po_name, '.', var_name]),
#                 'description': inspect.getdoc(variable),
#                 'arguments': inspect.getargspec(variable).args,
#                 'code': inspect.getsource(variable)
#             }
#             function_list.append(new_function)
#         elif isinstance(variable, tuple):
#             # this is a web element tuple
#             new_element = {
#                 'element_name': var_name,
#                 'element_selector': variable[0],
#                 'element_value': variable[1],
#                 'element_display_name': variable[2],
#                 'element_full_name': ''.join([full_po_name, '.', var_name])
#             }
#             element_list.append(new_element)
#         else:
#             print('ERROR')
#     page_object_data = {
#         'function_list': function_list,
#         'element_list': element_list,
#         'import_lines': import_lines
#     }
#     return page_object_data


def format_list_items(list_items):
    list_string = ''
    if list_items:
        for item in list_items:
            list_string = list_string + "    '" + item + "',\n"
        list_string = "[\n    {}\n]".format(list_string.strip()[:-1])
    else:
        list_string = '[]'
    return list_string


def save_suite(root_path, project, suite, test_cases, workers, browsers):
    suite_path = os.path.join(root_path, 'projects', project, 'test_suites',
                                    '{}.py'.format(suite))
    with open(suite_path, 'w', encoding='utf-8') as f:
        f.write('\n\n')
        f.write('browsers = {}\n'.format(format_list_items(browsers)))
        f.write('\n')
        f.write('workers = {}'.format(workers))
        f.write('\n\n')
        f.write('test_case_list = {}\n'.format(format_list_items(test_cases)))


# def is_page_object(parameter, root_path, project):
#     # identify if a parameter is a page object
#     path = os.path.join(root_path, 'projects', project, 'pages')
#     page_objects = utils.get_files_in_directory_dotted_path(path)
#     page_object_chain = '.'.join(parameter.split('.')[:-1])
#     if page_object_chain in page_objects:
#         return True
#     else:
#         return False


def new_suite(root_path, project, suite_name):
    errors = []
    if gui_utils.file_already_exists(root_path, project, 'test_suites', [], suite_name):
        errors.append('A file with that name already exists')

    if not errors:
        suite_path = os.path.join(root_path, 'projects', project, 'test_suites')
        # if not os.path.exists(suite_path):
        #     os.makedirs(suite_path)
        suite_full_path = os.path.join(suite_path, suite_name + '.py')

        with open(suite_full_path, 'w') as f:
            f.write(test_case_content)
    return errors


test_case_content = """

browsers = []

workers = 1

test_case_list = []
"""
