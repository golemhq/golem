import os

from golem.gui import gui_utils

def get_web_elements(content, po_name):
    elements = []

    for line in content:
        if '=' in line:
            element_name = line.split('=')[0].strip()
            element_description = line.split('=')[1].strip()
            element_selector = element_description.split(',')[0].strip().replace('\'','').replace('(','')
            element_value = element_description.split(',')[1].strip().replace('\'','')
            element_display_name = element_description.split(',')[2].strip().replace('\'','').replace(')', '')
            elements.append({
                'element_name': element_name,
                'element_selector': element_selector,
                'element_value': element_value,
                'element_display_name': element_display_name,
                'element_full_name': ''.join([po_name, '.', element_name])
                })
    return elements


def get_page_object_elements(root_path, project, po_name):
    path = os.path.join(
        root_path, 'projects', project, 'pages', po_name + '.py')

    with open(path) as f:
        content = f.readlines()
    
    web_elements = get_web_elements(content, po_name)

    return web_elements


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
    page_objects = gui_utils.get_page_objects(root_path, project)

    if len(parameter.split('.')) <= 1:
        return False
    else:
        page_object_chain = parameter.split('.')[0:-1]
        for po in page_objects:
            if po['name'] == page_object_chain[-1]:
                return True
    return False


def new_page_object(root_path, project, page_object_name):
    page_object_path = os.path.join(
        root_path, 'projects', project, 'pages', page_object_name + '.py')
    
    with open(page_object_path, 'w') as f:
        f.write('')