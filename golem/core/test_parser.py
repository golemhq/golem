import ast
import inspect
import re
import uuid


def parse_function_steps(function):
    """Get a list of parsed steps of a function.
    step:
      type: code-block | function-call
      code
    for step type == 'function-call':
      function_name
      parameters
    """
    code = function_body_code(function)

    # remove indentation
    code_lines = code.splitlines()
    indentation = len(code_lines[0]) - len(code_lines[0].lstrip())
    code_lines = [line[indentation:] for line in code_lines]
    code = '\n'.join(code_lines)

    if code.strip() == 'pass':
        return []

    replacements = []
    # replace parentheses
    code, replacements_ = _replace_substrings(code, '(', ')')
    replacements += replacements_
    # replace brackets
    code, replacements_ = _replace_substrings(code, '[', ']')
    replacements += replacements_
    # replace curly brackets
    code, replacements_ = _replace_substrings(code, '{', '}')
    replacements += replacements_
    # replace single quote multi-line strings
    pattern = re.compile(r'(\'\'\'.+?\'\'\')', re.S)
    code, replacements_ = _replace_re_pattern(code, pattern)
    replacements += replacements_
    # replace double quote multi-line strings
    pattern = re.compile(r'(\"\"\".+?\"\"\")', re.S)
    code, replacements_ = _replace_re_pattern(code, pattern)
    replacements += replacements_

    blocks = _split_code_into_blocks(code)

    # classify blocks into function calls and non function calls
    steps = []
    for block in blocks:
        if _code_block_is_function_call(block):
            steps.append({'type': 'function-call', 'code': block})
        else:
            steps.append({'type': 'code-block', 'code': block})
    # replace code back to original values
    for step in steps:
        step_code = step['code']
        for rep in list(reversed(replacements)):
            if rep[0] in step_code:
                step_code = step_code.replace(rep[0], rep[1])
        step['code'] = step_code
    # parse function call name and parameters
    for step in steps:
        if step['type'] == 'function-call':
            name, params = _parse_function_call(step['code'].replace('\n', ''))
            step['function_name'] = name
            step['parameters'] = params
    return steps


def function_body_code(function):
    """Get the code of the body of a function as a string"""
    source = inspect.getsource(function)
    pattern = re.compile(r'\s*def\s+\w+\s*\(.*?\)\s*:\s*\n', flags=re.S)
    return re.sub(pattern, '', source)


def _replace_substrings(code, first_char, last_char):
    """Replace the substrings between first_char and last_char
    with a unique id.
    Return the replaced string and a list of replacement
    tuples: (unique_id, original_substring)
    """
    substrings = []
    level = 0
    start = -1
    for i in range(len(code)):
        if code[i] == first_char:
            level += 1
            if level == 1:
                start = i
        if code[i] == last_char:
            level -= 1
            if level == 0:
                substrings.append((start, i + 1))
    code_ = code
    replacements = []
    for substr_index in substrings:
        unique_id = '{}"{}"{}'.format(first_char, str(uuid.uuid4()), last_char)
        substring = code[substr_index[0]:substr_index[1]]
        code_ = code_.replace(substring, unique_id)
        replacements.append((unique_id, substring))
    return code_, replacements


def _replace_re_pattern(code, pattern):
    """Replace the given re pattern with a unique id.
    Return the replaced string and a list of replacement
    tuples: (unique_id, original_substring)
    """
    replacements = []
    matches = re.findall(pattern, code)
    code_ = code
    for m in matches:
        unique_id = '"{}"'.format(str(uuid.uuid4()))
        code_ = code_.replace(m, unique_id)
        replacements.append((unique_id, m))
    return code_, replacements


def _split_code_into_blocks(code):
    """Split a string of Python code into the top level
    code blocks.
    Assumes there are no multi-line expressions
    """
    blocks = []
    code_lines = code.splitlines()
    # remove empty lines
    code_lines = [line for line in code_lines if len(line.strip())]
    block = None
    for line in code_lines:
        if block is None:
            block = line + '\n'
        elif (len(line) - len(line.lstrip()) > 0
                or re.match(r'^elif', line)
                or re.match(r'^else:', line)
                or re.match(r'^except', line)
                or re.match(r'^finally', line)):
            block += line + '\n'
        elif len(line) - len(line.lstrip()) == 0:
            blocks.append(block)
            block = line + '\n'
    if block is not None:
        blocks.append(block)
    # remove last new line character
    blocks = [b.strip() for b in blocks]
    return blocks


def _code_block_is_function_call(block):
    parsed = ast.parse(block.lstrip())
    if len(parsed.body) == 1 and type(parsed.body[0]) is ast.Expr:
        if hasattr(parsed.body[0], 'value'):
            if type(parsed.body[0].value) is ast.Call:
                sub_function_call = re.search(r'.*\(.*\)\.', block)
                if not sub_function_call:
                    return True
    return False


def _parse_function_call(step):
    """Parse a function call.
    Return its name and the list of parameters
    """
    method_name = step.split('(', 1)[0].strip()
    parameters = []
    pattern = re.compile(r'\((?P<args>.+)\)', flags=re.S)
    params_search = pattern.search(step)
    if params_search:
        params_string = params_search.group('args').strip()
        quote = False
        double_quote = False
        parenthesis = 0
        bracket = 0
        curly = 0
        start = 0
        for i in range(len(params_string)):
            char = params_string[i]
            if char == '\'':
                quote = not quote
            if char == '\"':
                double_quote = not double_quote
            if char == '(':
                parenthesis += 1
            if char == '{':
                curly += 1
            if char == '[':
                bracket += 1
            if char == ')':
                parenthesis -= 1
            if char == '}':
                curly -= 1
            if char == ']':
                bracket -= 1
            if char == ',':
                if not any([quote, double_quote, parenthesis, curly, bracket]):
                    parameters.append(params_string[start:i])
                    start = i + 1
            if i + 1 == len(params_string):
                parameters.append(params_string[start:i+1])
        parameters = [x.strip() for x in parameters]
    return method_name, parameters


def parse_imported_pages(code):
    """Extract imported pages from test code.
    The import statements must have the following format:
      `from projects.<project_name>.pages[.parents] import page1[, page2]`
    """
    page_list = []
    pattern = re.compile(r'from projects.*pages\.?(.* import +[^*\n]+)\n')
    groups = re.findall(pattern, code)
    for group in groups:
        parents = group.split('import')[0]
        pages = group.split('import')[1]
        pages = pages.split(',')
        for page in pages:
            if parents.strip():
                page_list.append('.'.join([parents.strip(), page.strip()]))
            else:
                page_list.append(page.strip())
    return page_list
