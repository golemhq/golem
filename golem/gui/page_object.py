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


def get_page_object_content(root_path, project, full_po_name):
    po, parents = utils.separate_file_from_parents(full_po_name)

    modulex = importlib.import_module('projects.{0}.pages.{1}'
                                      .format(project, full_po_name))
    variable_list = [item for item in dir(modulex) if not item.startswith("__")]
    element_list = []
    function_list = []
    import_lines = []
    code_line_list = []
    source_code = ''
     # get all the import lines in a list
    try:
        source_code = inspect.getsource(modulex)
    except:
        pass
    code_line_list = source_code.split('\n')
    for line in code_line_list:
        if 'import' in line:
            import_lines.append(line)
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
        elif isinstance(variable, tuple):
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
            print('ERROR')
    page_object_data = {
        'function_list': function_list,
        'element_list': element_list,
        'import_lines': import_lines,
        'code_line_list': code_line_list,
        'source_code': source_code
    }
    return page_object_data


def save_page_object(root_path, project, full_page_name,
                     elements, functions, import_lines):
    page_name, parents = utils.separate_file_from_parents(full_page_name)
    page_object_path = os.path.join(root_path,
                                    'projects',
                                    project,
                                    'pages',
                                    os.sep.join(parents),
                                    '{}.py'.format(page_name))
    with open(page_object_path, 'w', encoding='utf-8') as f:
        for line in import_lines:
            f.write("{}\n".format(line))
        for element in elements:
            f.write("\n\n{0} = ('{1}', \"{2}\", '{3}')".format(
                    element['name'],
                    element['selector'],
                    element['value'],
                    element['display_name']))
        for func in functions:
            f.write('\n\n' + func)


def is_page_object(parameter, root_path, project):
    # identify if a parameter is a page object
    path = os.path.join(root_path, 'projects', project, 'pages')
    page_objects = utils.get_files_in_directory_dotted_path(path)
    page_object_chain = '.'.join(parameter.split('.')[:-1])
    if page_object_chain in page_objects:
        return True
    else:
        return False


def new_page_object(root_path, project, parents, po_name):
    errors = []
    if gui_utils.file_already_exists(root_path, project, 'page_objects', parents, po_name):
        errors.append('A file with that name already exists')

    if not errors:
        parents_joined = os.sep.join(parents)
        base_path = os.path.join(root_path, 'projects', project, 'pages')
        page_object_path = os.path.join(base_path, parents_joined)
        
        # create the directory structure (with __init__.py files) if it does not exist
        if not os.path.exists(page_object_path):
            for parent in parents:
                base_path = os.path.join(base_path, parent)
                utils.create_new_directory(path=base_path, add_init=True)

        page_object_full_path = os.path.join(page_object_path, po_name + '.py')

        with open(page_object_full_path, 'w') as f:
            f.write('')
    return errors
