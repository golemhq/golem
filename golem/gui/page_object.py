import importlib
import os

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


def get_page_object_elements(root_path, project, full_po_name):
    po, parents = utils.separate_file_from_parents(full_po_name)

    path = os.path.join(root_path,
                        'projects',
                        project, 
                        'pages',
                        os.sep.join(parents),
                        '{}.py'.format(po))

    modulex = importlib.import_module('projects.{0}.pages.{1}'
                                      .format(project, full_po_name))
    variable_list = [item for item in dir(modulex) if not item.startswith("__")]
    element_list = []
    for var in variable_list:
        var_values = getattr(modulex, var)
        new_element = {
            'element_name': var,
            'element_selector': var_values[0],
            'element_value': var_values[1],
            'element_display_name': var_values[2],
            'element_full_name': ''.join([full_po_name, '.', var])
        }
        element_list.append(new_element)

    return element_list


def save_page_object(root_path, project, page_name, elements):
    page_object_path = os.path.join(
        root_path, 'projects', project, 'pages', page_name + '.py')

    with open(page_object_path, 'w') as f:
        for element in elements:
            print element
            f.write("{0} = ('{1}', '{2}', '{3}')\n".format(
                    element['name'],
                    element['selector'],
                    element['value'],
                    element['display_name']))


def is_page_object(parameter, root_path, project):
    # identify if a parameter is a page object
    page_objects = gui_utils.get_page_objects__DEPRECADO(root_path, project)
    print parameter
    if len(parameter.split('.')) <= 1:
        return False
    else:
        page_object_chain = parameter.split('.')[0:-1]
        for po in page_objects:
            if po['name'] == page_object_chain[-1]:
                return True
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