import ast


def ast_parse_file(filename):
    """Parse a Python file using ast.
    Returns a ast.Module node
    """
    with open(filename, "rt", encoding='utf-8') as file:
        return ast.parse(file.read(), filename=filename)


def top_level_functions(ast_node):
    """Given an ast.Module node return the names of the top level functions"""
    return [f.name for f in ast_node.body if isinstance(f, ast.FunctionDef)]


def top_level_assignments(ast_node):
    """Given an ast Module node,
    return the names of the top level assignments.
    e.g.: "foo = 2" -> returns ['foo']
    https://greentreesnakes.readthedocs.io/en/latest/nodes.html#Assign
    """
    assignments = []
    for v in ast_node.body:
        if type(v) == ast.Assign:
            if len(v.targets) == 1:
                assignments.append(v.targets[0].id)
    return assignments
