import os


def rename_file(old_path, old_file, new_path, new_file):
    """rename a file
    If there are no errors, returns an empty string.
    If there are errors return a string with the error description"""
    error = ''
    os.makedirs(new_path, exist_ok=True)
    old_fullpath = os.path.join(old_path, old_file)
    new_fullpath = os.path.join(new_path, new_file)
    if os.path.isfile(new_fullpath):
        error = 'File {} already exists'.format(new_fullpath)
    else:
        try:
            os.rename(old_fullpath, new_fullpath)
        except:
            error = 'There was an error renaming \'{}\' to \'{}\''.format(
                        old_fullpath, new_fullpath)
    return error


def new_directory(root_path, project, parents, dir_name, dir_type):
    """Creates a new directory for suites, tests or pages.
    If the directory is inside other directories, these should already exist.
    parents is a list of parent directories.
    dir_type should be in ['tests', 'suites', 'pages']"""
    parents = os.sep.join(parents)
    path = os.path.join(root_path, 'projects', project, dir_type, parents, dir_name)
    errors = []
    if os.path.exists(path):
        errors.append('A directory with that name already exists')
    else:
        utils.create_new_directory(path=path, add_init=True)
    return errors