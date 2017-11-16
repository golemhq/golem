import importlib
import os
import types
import inspect

from golem.core import utils



def page_exists(root_path, project, full_page_name):
    page_rel_path = os.sep.join(full_page_name.split('.'))
    path = os.path.join(root_path, 'projects', project, 'pages', page_rel_path + '.py')
    return os.path.isfile(path)


def get_page_object_content(project, full_page_name):
    modulex = importlib.import_module('projects.{0}.pages.{1}'.format(project, full_page_name))
    # get all the names of the module, ignoring the ones starting with '_'
    variable_list = [item for item in dir(modulex) if not item.startswith("_")]
    element_list = []
    function_list = []
    import_lines = []
    code_line_list = []
    source_code = ''
    # get all the import lines in a list
    try:
        source_code = inspect.getsource(modulex)
    except:
        print('Parsing of {} failed'.format(full_page_name))
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
                'full_function_name': ''.join([full_page_name, '.', var_name]),
                'description': inspect.getdoc(variable),
                'arguments': list(inspect.signature(variable).parameters),
                'code': inspect.getsource(variable)
            }
            function_list.append(new_function)
        elif isinstance(variable, tuple):
            # this is a web element tuple
            if len(variable) >= 2:
                element_display_name = ''
                if len(variable) >= 3:
                    element_display_name = variable[2]
                new_element = {
                    'element_name': var_name,
                    'element_selector': variable[0],
                    'element_value': variable[1],
                    'element_display_name': element_display_name,
                    'element_full_name': ''.join([full_page_name, '.', var_name])
                }
                element_list.append(new_element)
        # elif isinstance(variable, types.ModuleType):
        #     pass
        else:
            pass
            # print('ERROR', variable)
    page_object_data = {
        'function_list': function_list,
        'element_list': element_list,
        'import_lines': import_lines,
        'code_line_list': code_line_list,
        'source_code': source_code
    }
    return page_object_data


def save_page_object(root_path, project, full_page_name, elements, functions, import_lines):
    page_name, parents = utils.separate_file_from_parents(full_page_name)
    page_object_path = os.path.join(root_path, 'projects', project, 'pages',
                                    os.sep.join(parents), '{}.py'.format(page_name))
    with open(page_object_path, 'w', encoding='utf-8') as po_file:
        for line in import_lines:
            po_file.write("{}\n".format(line))
        for element in elements:
            # replace the spaces with underlines of the element name
            if ' ' in element['name']:
                element['name'] = element['name'].replace(' ', '_')
            element['value'] = element['value'].replace('"', '\\"').replace("'", "\\'")
            po_file.write("\n\n{0} = ('{1}', \'{2}\', '{3}')".format(element['name'],
                                                                     element['selector'],
                                                                     element['value'],
                                                                     element['display_name']))
        for func in functions:
            po_file.write('\n\n' + func)


def save_page_object_code(root_path, project, full_page_name, content):
    page_name, parents = utils.separate_file_from_parents(full_page_name)
    page_path = os.path.join(root_path, 'projects', project, 'pages',
                             os.sep.join(parents), '{}.py'.format(page_name))
    with open(page_path, 'w', encoding='utf-8') as po_file:
        po_file.write(content)


def is_page_object(parameter, root_path, project):
    # identify if a parameter is a page object
    path = os.path.join(root_path, 'projects', project, 'pages')
    page_objects = utils.get_files_in_directory_dot_path(path)
    page_object_chain = '.'.join(parameter.split('.')[:-1])
    return bool(page_object_chain in page_objects)


def new_page_object(root_path, project, parents, page_name, add_parents=False):
    """Create a new page object.
    Parents is a list of directories and subdirectories where the page should be 
    placed.
    if add_parents is true, the parent directories will be added if they do not exist."""
    errors = []

    full_page_path = os.path.join(root_path, 'projects', project, 'pages',
                             os.sep.join(parents), '{}.py'.format(page_name))

    if os.path.isfile(full_page_path):
        errors.append('A page file with that name already exists')
    
    if not errors:
        page_path = os.path.join(root_path, 'projects', project,
                                 'pages', os.sep.join(parents))
        if not os.path.exists(page_path):
            if add_parents:
                base_path = os.path.join(root_path, 'projects', project, 'pages')
                for parent in parents:
                    base_path = os.path.join(base_path, parent)
                    if not os.path.exists(base_path):
                        utils.create_new_directory(path=base_path, add_init=True)
            else:
                errors.append('Directory for new page does not exist')

    if not errors:
        with open(full_page_path, 'w') as po_file:
            po_file.write('')
    return errors
