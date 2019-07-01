"""Utils for the test_runner module."""
import os
import types

from golem.core import utils


def import_page_into_test(base_path, parent_module, page_path_list):
    """Import a page module into a (test) module provided
    the relative dot path to the page.
    """
    if len(page_path_list) > 1:
        new_node_name = page_path_list.pop(0)
        if not hasattr(parent_module, new_node_name):
            new_module = types.ModuleType(new_node_name)
            setattr(parent_module, new_node_name, new_module)
        else:
            new_module = getattr(parent_module, new_node_name)
        base_path = os.path.join(base_path, new_node_name)
        new_module = import_page_into_test(base_path, new_module, page_path_list)
        setattr(parent_module, new_node_name, new_module)
    else:
        path = os.path.join(base_path, page_path_list[0] + '.py')
        imported_module, error = utils.import_module(path)
        if error:
            raise ImportError(error)
        setattr(parent_module, page_path_list[0], imported_module)
    return parent_module

