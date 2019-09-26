import os
import shutil

from golem.core import session


def _directory_element(elem_type, name, dot_path=None):
    """instantiate directory element dictionary"""
    element = {
        'type': elem_type,
        'name': name,
        'dot_path': dot_path,
        'sub_elements': []
    }
    return element


def generate_file_structure_dict(full_path, original_path=None):
    """Generates a dictionary with the preserved structure of a given
    directory.
    Files are stored in tuples, with the first element being the name
    of the file without its extention and the second element
    the dot path to the file.

    For example, given the following directory:
    test/
         subdir1/
                 subdir2/
                         file3
                 file2
         file1

    The result will be:
    test = {
        'subdir1': {
            'subdir2': {
                'subdir2': {
                    ('file3', 'subdir1.subdir2.file3'): None,
                },
                ('file2', 'subdir1.file2'): None,
        },
        ('file1', 'file1'): None,
    }
    """
    root_dir_name = os.path.basename(os.path.normpath(full_path))
    if not original_path:
        original_path = full_path
    rel_path = os.path.relpath(full_path, original_path).replace(os.sep, '.')
    rel_dot_path = '' if rel_path == '.' else rel_path.replace(os.sep, '.')
    element = _directory_element('directory', root_dir_name, rel_dot_path)

    all_sub_elements = os.listdir(full_path)
    files = []
    directories = []
    for elem in all_sub_elements: 
        if os.path.isdir(os.path.join(full_path, elem)):
            if elem not in ['__pycache__']:
                directories.append(elem)
        else:
            cond1 = elem not in ['__init__.py', '.DS_Store']
            cond2 = not elem.endswith('.csv')
            if cond1 and cond2:
                files.append(os.path.splitext(elem)[0])
    for directory in directories:
        sub_element = generate_file_structure_dict(os.path.join(full_path, directory),
                                                   original_path)
        element['sub_elements'].append(sub_element)
    for filename in sorted(files):
        full_file_path = os.path.join(full_path, filename)

        rel_file_path = os.path.relpath(full_file_path, original_path)
        dot_file_path = rel_file_path.replace(os.sep, '.')
        file_element = _directory_element('file', filename, dot_file_path)
        element['sub_elements'].append(file_element)

    return element


def get_files_dot_path(base_path, extension=None):
    """generate a list of all the files inside a directory and
    subdirectories with the relative path as a dotted string.
    for example, given the files:
      C:/base_dir/dir/file1.py
      C:/base_dir/dir/sub_dir/file2.py
      > get_files_in_directory_dotted_path('C:/base_dir/')
      > ['dir.file1', 'dir.sub_dir.file2']
    """
    all_files = []
    files_with_dotted_path = []
    for path, subdirs, files in os.walk(base_path):
        if '__pycache__' not in path:
            for name in files:
                if name not in ['__init__.py', '.DS_Store']:
                    root, ext = os.path.splitext(name)
                    if extension and ext != extension:
                        continue
                    filepath = os.path.join(path, root)
                    all_files.append(filepath)
    for file in all_files:
        rel_path_as_list = file.replace(base_path, '').split(os.sep)
        rel_path_as_list = [x for x in rel_path_as_list if x != '']
        files_with_dotted_path.append('.'.join(rel_path_as_list))
    return files_with_dotted_path


def create_directory(path_list=None, path=None, add_init=False):
    """crate an empty directory with the option to add an __init__.py
    file inside it
    """
    if path_list:
        path = os.sep.join(path_list)
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)
    if add_init:
        # add __init__.py file to make the new directory a python package
        init_path = os.path.join(path, '__init__.py')
        open(init_path, 'a').close()


def create_package(path_list=None, path=None):
    create_directory(path_list, path, add_init=True)


def rename_file(old_path, new_path):
    errors = []
    if not os.path.isfile(old_path):
        errors.append('File {} does not exist'.format(old_path))
    elif os.path.isfile(new_path):
        errors.append('A file with that name already exists')
    else:
        try:
            os.makedirs(os.path.dirname(new_path), exist_ok=True)
            os.rename(old_path, new_path)
        except:
            errors.append('There was an error renaming file')
    return errors


def new_directory_of_type(project, parents, dir_name, dir_type):
    """Creates a new directory for suites, tests or pages.
    If the directory is inside other directories, these should already exist.
    parents is a list of parent directories.
    dir_type should be in ['tests', 'suites', 'pages']"""
    errors = []
    if dir_type not in ['tests', 'suites', 'pages']:
        errors.append('{} is not a valid dir_type'.format(dir_type))
    else:
        parents = os.sep.join(parents)
        path = os.path.join(session.testdir, 'projects', project, dir_type, parents, dir_name)
        if os.path.exists(path):
            errors.append('A directory with that name already exists')
        else:
            create_directory(path=path, add_init=True)
    return errors


def create_package_directories(base_path, rel_path):
    """Create nested Python packages if they don't
    exist given a base path and a relative path
    """
    dirs = rel_path.split(os.sep)
    for dir_ in dirs:
        base_path = os.path.join(base_path, dir_)
        if not os.path.isdir(base_path):
            create_package(path=base_path)


def rename_directory(basepath, src, dst):
    """Rename a directory folder.
    src and dst must be relative paths to basepath.
    src must exists and be a directory.
    dst must not exist.
    """
    errors = []
    srcpath = os.path.join(basepath, src)
    dstpath = os.path.join(basepath, dst)
    if not os.path.exists(srcpath):
        errors.append('Directory {} does not exist'.format(src))
    elif not os.path.isdir(srcpath):
        errors.append('Path {} is not a directory'.format(src))
    elif os.path.exists(dstpath):
        errors.append('Path {} already exists'.format(dst))
    else:
        try:
            dirname = os.path.dirname(dst)
            if dirname:
                create_package_directories(basepath, dirname)
            os.rename(srcpath, dstpath)
        except PermissionError:
            errors.append('Error: PermissionError')
        except Exception as e:
            errors.append('An error occurred while renaming folder')
    return errors


def delete_directory(dirpath):
    """Delete a directory"""
    errors = []
    if not os.path.isdir(dirpath):
        errors.append('Directory does not exist')
    else:
        try:
            shutil.rmtree(dirpath, ignore_errors=False)
        except PermissionError:
            errors.append('Error: PermissionError')
        except Exception:
            errors.append('An error occurred while renaming folder')
    return errors


def path_is_parent_of_path(path, second_path):
    """Return whether the first path is a parent of the
    second path.
    """
    os_sep_path = path.split(os.sep)
    os_sep_second_path = second_path.split(os.sep)
    if len(os_sep_path) >= len(os_sep_second_path):
        return False
    else:
        for i, x in enumerate(os_sep_path):
            if x != os_sep_second_path[i]:
                return False
        return True
