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
