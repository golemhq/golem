import inspect
import os
import re
import shutil
import types

from golem.core import file_manager
from golem.core.project import Project, validate_project_element_name, BaseProjectElement


def create_page(project_name, page_name):
    errors = []
    page_name = page_name.strip().replace(' ', '_')
    project = Project(project_name)
    if page_name in project.pages():
        errors.append('A page with that name already exists')
    else:
        errors = validate_project_element_name(page_name)
    if not errors:
        project.create_packages_for_element(page_name, 'page')
        with open(Page(project_name, page_name).path, 'w') as f:
            f.write('')
    return errors


def rename_page(project_name, page_name, new_page_name):
    errors = []
    project = Project(project_name)
    new_page_name = new_page_name.strip().replace(' ', '_')
    if page_name not in project.pages():
        errors.append('Page {} does not exist'.format(page_name))
    else:
        errors = validate_project_element_name(new_page_name)
    if not errors:
        old_path = Page(project_name, page_name).path
        new_path = Page(project_name, new_page_name).path
        project.create_packages_for_element(new_page_name, 'page')
        errors = file_manager.rename_file(old_path, new_path)
    return errors


def duplicate_page(project, name, new_name):
    errors = []
    old_path = Page(project, name).path
    new_path = Page(project, new_name).path
    new_name = new_name.strip().replace(' ', '_')
    if name == new_name:
        errors.append('New page name cannot be the same as the original')
    elif not os.path.isfile(old_path):
        errors.append('Page {} does not exist'.format(name))
    elif os.path.isfile(new_path):
        errors.append('A page with that name already exists')
    else:
        errors = validate_project_element_name(new_name)
    if not errors:
        try:
            Project(project).create_packages_for_element(new_name, 'page')
            shutil.copyfile(old_path, new_path)
        except:
            errors.append('There was an error creating the new page')
    return errors


def edit_page(project, page_name, elements, functions, import_lines):
    def format_element_string(name, selector, value, display_name):
        with_format = ("\n\n{0} = ('{1}', \'{2}\', '{3}')"
                       .format(name, selector, value, display_name))
        return with_format

    path = Page(project, page_name).path
    with open(path, 'w') as f:
        for line in import_lines:
            f.write("{}\n".format(line))
        for element in elements:
            # replace the spaces in web element names with underscores
            element['name'] = element['name'].replace(' ', '_')
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
    with open(Page(project, page_name).path, 'w') as f:
        f.write(content)


def delete_page(project, page):
    errors = []
    path = Page(project, page).path
    if not os.path.isfile(path):
        errors.append('Page {} does not exist'.format(page))
    else:
        try:
            os.remove(path)
        except:
            errors.append('There was an error removing file {}'.format(page))
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
        # get all the names of the module,
        # ignoring the ones starting with '_'
        variable_list = [i for i in dir(module) if not i.startswith("_")]
        components['source_code'] = self.code
        components['code_lines'] = components['source_code'].split('\n')
        # parse import lines
        patterns = (
            re.compile(r'(from .*? import [^\n(]*)\n'),
            re.compile(r'^(import [^\n]*)\n', flags=re.MULTILINE),
            re.compile(r'(from [^\n]+ import \(.*?\))', re.DOTALL)
        )
        if len(components['source_code']):
            for pattern in patterns:
                result = re.search(pattern, components['source_code'])
                if result:
                    components['import_lines'] += list(result.groups())

        for var_name in variable_list:
            variable = getattr(module, var_name)
            if isinstance(variable, types.FunctionType):
                # function
                partial_name = '{}.{}'.format(self.name.split('.')[-1], var_name)
                function = {
                    'name': var_name,
                    'partial_name': partial_name,
                    'full_name': '{}.{}'.format(self.name, var_name),
                    'description': inspect.getdoc(variable),
                    'arguments': list(inspect.signature(variable).parameters),
                    'code': inspect.getsource(variable)
                }
                components['functions'].append(function)
            elif isinstance(variable, tuple):
                # web element tuple
                if len(variable) >= 2:
                    display_name = ''
                    if len(variable) >= 3:
                        display_name = variable[2]
                    partial_name = '{}.{}'.format(self.name.split('.')[-1], var_name)
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
