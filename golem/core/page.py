import inspect
import os
import re
import shutil
import types

from golem.core import file_manager
from golem.core import parsing_utils
from golem.core.project import BaseProjectElement
from golem.core.project import Project
from golem.core.project import validate_project_element_name


def create_page(project_name, page_name):
    errors = []
    project = Project(project_name)
    if page_name in project.pages():
        errors.append('A page with that name already exists')
    else:
        errors = validate_project_element_name(page_name)
    if not errors:
        project.create_packages_for_element(page_name, project.file_types.PAGE)
        with open(Page(project_name, page_name).path, 'w', encoding='utf-8') as f:
            f.write('')
    return errors


def rename_page(project_name, page_name, new_page_name):
    errors = []
    project = Project(project_name)
    if page_name not in project.pages():
        errors.append(f'Page {page_name} does not exist')
    else:
        errors = validate_project_element_name(new_page_name)
    if not errors:
        old_path = Page(project_name, page_name).path
        new_path = Page(project_name, new_page_name).path
        project.create_packages_for_element(new_page_name, project.file_types.PAGE)
        errors = file_manager.rename_file(old_path, new_path)
    return errors


def duplicate_page(project, name, new_name):
    errors = []
    old_path = Page(project, name).path
    new_path = Page(project, new_name).path
    if name == new_name:
        errors.append('New page name cannot be the same as the original')
    elif not os.path.isfile(old_path):
        errors.append(f'Page {name} does not exist')
    elif os.path.isfile(new_path):
        errors.append('A page with that name already exists')
    else:
        errors = validate_project_element_name(new_name)
    if not errors:
        try:
            Project(project).create_packages_for_element(new_name, Project.file_types.PAGE)
            shutil.copyfile(old_path, new_path)
        except:
            errors.append('There was an error creating the new page')
    return errors


def edit_page(project, page_name, elements, functions, import_lines):
    def format_element_string(name, selector, value, display_name):
        return f"\n\n{name} = ('{selector}', \'{value}\', '{display_name}')"

    path = Page(project, page_name).path
    with open(path, 'w', encoding='utf-8') as f:
        for line in import_lines:
            f.write(f"{line}\n")
        for element in elements:
            # replace the spaces in web element names with underscores
            element['name'] = element['name'].replace(' ', '_')

            if element['value']:
                if element['value'][0] == '\'' and element['value'][-1] == '\'':
                    # remove first and last single quotes if present
                    element['value'] = element['value'][1:-1]
                elif element['value'].startswith('"""') and element['value'].endswith('"""')\
                        and len(element['value']) >= 6:
                    # remove first and last triple double quotes if present
                    element['value'] = element['value'][3:-3]
                elif element['value'][0] == '"' and element['value'][-1] == '"':
                    # remove first and last double quotes if present
                    element['value'] = element['value'][1:-1]
                # escape quote characters
                element['value'] = element['value'].replace('"', '\\"').replace("'", "\\'")

            if not element['display_name']:
                element['display_name'] = element['name']
            formatted = format_element_string(element['name'], element['selector'],
                                              element['value'], element['display_name'])
            f.write(formatted)
        for func in functions:
            f.write('\n\n' + func)


def edit_page_code(project, page_name, content):
    """Edit Page code.
    content must be the file content as string
    """
    with open(Page(project, page_name).path, 'w', encoding='utf-8') as f:
        f.write(content)


def delete_page(project, page):
    errors = []
    path = Page(project, page).path
    if not os.path.isfile(path):
        errors.append(f'Page {page} does not exist')
    else:
        try:
            os.remove(path)
        except:
            errors.append(f'There was an error removing file {page}')
    return errors


class Page(BaseProjectElement):

    element_type = 'page'

    @property
    def components(self):
        """Parses a page and returns its components as a dictionary.

        Components:
          functions    :    list of functions
          elements     :    web elements defined inside page
          import_lines :    list of imported lines
          code_lines   :    source code lines
          source_code  :    source code as string

        Each function contains:
          name
          full_name
          description
          arguments
          code

        Each element contains:
          name
          selector
          value
          display_name
          full_name
        """
        components = {
            'functions': [],
            'elements': [],
            'import_lines': [],
            'code_lines': [],
            'source_code': ''
        }
        module = self.module
        components['source_code'] = self.code
        components['code_lines'] = components['source_code'].split('\n')

        # parse import lines  TODO: move to a function
        patterns = (
            re.compile(r'(from .*? import [^\n(]*)\n'),
            re.compile(r'^(import [^\n]*)\n', flags=re.MULTILINE),
            re.compile(r'(from [^\n]+ import \(.*?\))', re.DOTALL)
        )
        if len(components['source_code']):
            for pattern in patterns:
                result = re.findall(pattern, components['source_code'])
                if result:
                    components['import_lines'] += result

        ast_module_node = parsing_utils.ast_parse_file(self.path)
        local_functions = parsing_utils.top_level_functions(ast_module_node)
        local_assignments = parsing_utils.top_level_assignments(ast_module_node)

        # get all the names of the module,
        # ignoring the ones starting with '_'
        variable_list = [i for i in dir(module) if not i.startswith("_")]

        for var_name in variable_list:
            variable = getattr(module, var_name)
            if isinstance(variable, types.FunctionType) and var_name in local_functions:
                # function
                partial_name = f'{self.stem_name}.{var_name}'
                function = {
                    'name': var_name,
                    'partial_name': partial_name,
                    'full_name': f"{self.name}.{var_name}",
                    'description': inspect.getdoc(variable),
                    'arguments': list(inspect.signature(variable).parameters),
                    'code': inspect.getsource(variable)
                }
                components['functions'].append(function)
            elif isinstance(variable, tuple) and var_name in local_assignments:
                # web element tuple
                if len(variable) >= 2:
                    display_name = ''
                    if len(variable) >= 3:
                        display_name = variable[2]
                    partial_name = f'{self.stem_name}.{var_name}'
                    element = {
                        'name': var_name,
                        'selector': variable[0],
                        'value': variable[1],
                        'display_name': display_name,
                        'partial_name': partial_name,
                        'full_name': ''.join([self.name, '.', var_name])
                    }
                    components['elements'].append(element)
            else:
                pass
        return components
