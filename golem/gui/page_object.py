import importlib
import os
import types
import inspect

from golem.core import utils
from golem.gui import gui_utils


def get_web_elements(content, po_name):
    elements = []

    # for line in content:
    #     if '=' in line:
    #         element_name = line.split('=')[0].strip()
    #         element_description = line.split('=')[1].strip()
    #         element_selector = element_description.split(',')[0].strip().replace('\'','').replace('(','')
    #         element_value = element_description.split(',')[1].strip().replace('\'','')
    #         element_display_name = element_description.split(',')[2].strip().replace('\'','').replace(')', '')
    #         elements.append({
    #             'element_name': element_name,
    #             'element_selector': element_selector,
    #             'element_value': element_value,
    #             'element_display_name': element_display_name,
    #             'element_full_name': ''.join([po_name, '.', element_name])
    #             })
    return elements


def get_page_object_elements_and_functions(root_path, project, full_po_name):
    po, parents = utils.separate_file_from_parents(full_po_name)

    modulex = importlib.import_module('projects.{0}.pages.{1}'
                                      .format(project, full_po_name))
    variable_list = [item for item in dir(modulex) if not item.startswith("__")]
    element_list = []
    function_list = []
    for var_name in variable_list:
        variable = getattr(modulex, var_name)
        if isinstance(variable, types.FunctionType):
            # this is a function
            new_function = {
                'function_name': var_name,
                'full_function_name': ''.join([full_po_name, '.', var_name]),
                'description': inspect.getdoc(variable),
                'arguments': inspect.getargspec(variable).args,
                'code': inspect.getsource(variable)
            }
            function_list.append(new_function)
        elif isinstance(variable, types.TupleType):
            # this is a web element tuple
            new_element = {
                'element_name': var_name,
                'element_selector': variable[0],
                'element_value': variable[1],
                'element_display_name': variable[2],
                'element_full_name': ''.join([full_po_name, '.', var_name])
            }
            element_list.append(new_element)
        else:
            print 'ERROR'
    page_object_data = {
        'function_list': function_list,
        'element_list': element_list
    }
    return page_object_data


def save_page_object(root_path, project, page_name, elements, functions):
    page_object_path = os.path.join(
        root_path, 'projects', project, 'pages', page_name + '.py')

    print 'ELEMENTS', elements
    print 'FUNCTIONS', functions

    with open(page_object_path, 'w') as f:
        for element in elements:
            f.write("{0} = ('{1}', '{2}', '{3}')\n\n".format(
                    element['name'],
                    element['selector'],
                    element['value'],
                    element['display_name']))
        for func in functions:
            f.write(func + '\n\n')


def is_page_object(parameter, root_path, project):
    # identify if a parameter is a page object
    path = os.path.join(root_path, 'projects', projectname, 'pages')
    page_objects = utils.get_page_objects_as_list(path)
    page_object_chain = '.'.join(parameter.split('.')[:-1])
    if page_object_chain in page_objects:
        return True
    else:
        return False


def new_page_object(root_path, project, parents, page_object_name):
    parents_joined = os.sep.join(parents)

    page_object_path = os.path.join(
        root_path, 'projects', project, 'pages', parents_joined)
    if not os.path.exists(page_object_path):
        os.makedirs(page_object_path)
    page_object_full_path = os.path.join(page_object_path, page_object_name + '.py')
    
    with open(page_object_full_path, 'w') as f:
        f.write('')