"""Utils for the test_runner module."""
import importlib
import types


def import_page_into_test_module(project, parent_module, page_path, page_path_list=None):
    """Import a page module into a (test) module provided
    the relative dot path to the page.
    """
    if not page_path_list:
        page_path_list = page_path.split('.')
    if len(page_path_list) > 1:
        if not hasattr(parent_module, page_path_list[0]):
            new_module = types.ModuleType(page_path_list[0])
            setattr(parent_module, page_path_list[0], new_module)
        else:
            new_module = getattr(parent_module, page_path_list[0])
        page_path_list.pop(0)
        new_module = import_page_into_test_module(project, new_module,
                                                  page_path, page_path_list)
        setattr(parent_module, page_path_list[0], new_module)
    else:
        imported_module = importlib.import_module('projects.{}.pages.{}'
                                                  .format(project, page_path))
        setattr(parent_module, page_path_list[0], imported_module)
    return parent_module
