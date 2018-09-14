import os
import sys
import types
import inspect

from golem.core import utils, file_manager, test_execution


def page_exists(root_path, project, full_page_name):
    """Page object exists.
    full_page_name must be dot path from the /project/pages/ 
    directory
    Example: 
      testdir/projects/project1/pages/modulex/pagex.py
      page_exists(root_path, 'project1', 'modulex.pagex') -> True
    """
    page_rel_path = os.sep.join(full_page_name.split('.'))
    path = os.path.join(root_path, 'projects', project, 'pages',
                        page_rel_path + '.py')
    return os.path.isfile(path)

def _list_imported_functions(mod):
    return [func.__name__ for func in iter(mod.__dict__.values()) 
            if (inspect.isfunction(func) and inspect.getmodule(func) != None)]


def get_page_object_content(project, full_page_name):
    """Parses a page object and returns it's contents
    in dictionary format.
    
    Page Object Contents:
      functions :    list of functions
      elements  :    web elements defined inside page
      import lines : list of import lines
      source code :  source code as string

    Each function contains:
      function_name
      description
      arguments
      code

    Each element contains:
      element_selector
      element_value
      element_display_name
      element_full_name
    """
    po_data = {
        'functions': [],
        'elements': [],
        'import_lines': [],
        'code_lines': [],
        'source_code': ''
    }

    path = generate_page_path(test_execution.root_path, project, full_page_name)
    po_module, _ = utils.import_module(path)

    # get all the names of the module,
    # ignoring the ones starting with '_' and imported functions
    variable_list = [i for i in dir(po_module) if (i not in _list_imported_functions(po_module)) and not i.startswith("_")]
    
    # get all the import lines in a list
    try:
        po_data['source_code'] = inspect.getsource(po_module)
    except:
        pass
    if not po_data['source_code']:
        try:
            sys.modules['file_module'] = po_module
            po_data['source_code'] = inspect.getsource(po_module)
        except:
            print('Parsing of {} failed'.format(full_page_name))    
    po_data['code_lines'] = po_data['source_code'].split('\n')
    for line in po_data['code_lines']:
        if 'import' in line:
            po_data['import_lines'].append(line)
    for var_name in variable_list:
        variable = getattr(po_module, var_name)
        if isinstance(variable, types.FunctionType):
            # this is a function
            new_function = {
                'function_name': var_name,
                'full_function_name': ''.join([full_page_name, '.', var_name]),
                'description': inspect.getdoc(variable),
                'arguments': list(inspect.signature(variable).parameters),
                'code': inspect.getsource(variable)
            }
            po_data['functions'].append(new_function)
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
                po_data['elements'].append(new_element)
        # elif isinstance(variable, types.ModuleType):
        #     pass
        else:
            pass
    return po_data


def get_page_object_code(path):
    """Get the page object code as string given the full path
    to the python file"""
    code = ''
    if os.path.isfile(path):
        with open(path) as ff:
            code = ff.read()
    return code


def save_page_object(root_path, project, full_page_name, elements,
                     functions, import_lines):
    """Save Page Object contents to file.
    full_page_name must be a dot path starting from /project/pages/
    directory, (i.e.: 'module.sub_module.page_name_01')
    """
    def format_element_string(name, selector, value, display_name):
        formatted = ("\n\n{0} = ('{1}', \'{2}\', '{3}')"
                     .format(element['name'], element['selector'],
                             element['value'], element['display_name'])
                    )
        return formatted

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
            # escape quote characters
            element['value'] = element['value'].replace('"', '\\"').replace("'", "\\'")
            if not element['display_name']:
                element['display_name'] = element['name']
            formatted = format_element_string(element['name'],
                                              element['selector'],
                                              element['value'],
                                              element['display_name'])
            po_file.write(formatted)
        for func in functions:
            po_file.write('\n\n' + func)


def save_page_object_code(root_path, project, full_page_name, content):
    """Save a Page Object given it's full code as a string.
    full_page_name must be a dot path starting from /project/pages/
    directory.
    content must be the file content as string
    """
    page_name, parents = utils.separate_file_from_parents(full_page_name)
    page_path = os.path.join(root_path, 'projects', project, 'pages',
                             os.sep.join(parents), '{}.py'.format(page_name))
    with open(page_path, 'w', encoding='utf-8') as po_file:
        po_file.write(content)


def new_page_object(root_path, project, parents, page_name):
    """Create a new page object.
    Parents is a list of directories and subdirectories where the
    page should be stored.
    If add_parents is True, the parent directories will be added
    if they do not exist."""
    errors = []
    base_path = os.path.join(root_path, 'projects', project, 'pages')
    full_path = os.path.join(base_path, os.sep.join(parents))
    filepath = os.path.join(full_path, '{}.py'.format(page_name))
    if os.path.isfile(filepath):
        errors.append('A page file with that name already exists')
    if not errors:
        if not os.path.isdir(full_path):
            for parent in parents:
                base_path = os.path.join(base_path, parent)
                file_manager.create_directory(path=base_path,
                                              add_init=True)
        with open(filepath, 'w') as po_file:
            po_file.write('')
    return errors


def generate_page_path(root_path, project, full_page_name):
    """Generates a path to a page object python file
    Example":
      generate_page_path('user/testdir', 'project1, 'module1.page1')
      -> 'user/testdir/projects/project1/pages/module1/page1.py'
    """
    page_name, parents = utils.separate_file_from_parents(full_page_name)
    page_path = os.path.join(root_path, 'projects', project, 'pages',
                             os.sep.join(parents), '{}.py'.format(page_name))
    return page_path


def pages_base_dir(root_path, project):
    """Generate base dir for pages.
    i.e.: <root_path>/projets/<project>/pages/
    """
    return os.path.join(root_path, 'projects', project, 'pages')
