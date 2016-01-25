import csv
import os
import datetime


def read_global_settings():
    settings = {}
    settings_file = 'settings.ini'
    if os.path.exists(settings_file):
        execfile(settings_file, settings)
        settings.pop("__builtins__", None)
    else:
        raise Exception('File {} does not exist'.format(settings_file))
    return settings


def get_projects(path):
    projects = os.walk(os.path.join(path,'projects')).next()[1]
    if '.metadata' in projects: projects.remove('.metadata')
    if '.recommenders' in projects: projects.remove('.recommenders')
    return projects


# def go_one_level_deeper__DEPRECADO(file_structure, this_dir_file_structure, current_directory, parents):
#     first_parent = parents[0]
#     parents.pop(0)
#     if len(parents) == 0:

#         file_structure['childirs'][current_directory] = this_dir_file_structure
#     else: 
#         file_structure['childirs'][first_parent] = go_one_level_deeper(
#                                     file_structure['childirs'][first_parent],
#                                     this_dir_file_structure,
#                                     current_directory,
#                                     parents)
#     return file_structure


# def get_test_cases__DEPRECADO(workspace, project):
#     path = os.path.join(workspace, 'projects', project, 'test_cases')

#     file_structure = {
#         'name': '',
#         'files': [],
#         'childirs': {} }

#     for root, dirs, files in os.walk(path):
#         parents = root.replace(path, '').split(os.sep)
#         parents.pop(0)
#         current_directory = os.path.basename(root)
#         files = [x[:-3] for x in files]
#         if '__init__' in files: files.remove('__init__')
#         this_dir_file_structure = {
#                                     'name': current_directory,
#                                     'files': files,
#                                     'childirs': {} }
#         if len(parents) == 0:
#             file_structure = this_dir_file_structure
#         else:
#             file_structure = go_one_level_deeper(
#                                         file_structure, 
#                                         this_dir_file_structure, 
#                                         current_directory,
#                                         parents)

#     return file_structure


def get_test_cases_or_page_objects(workspace, project, root_dir):
    path = os.path.join(workspace, 'projects', project, root_dir)

    dir = {}
    rootdir = path.rstrip(os.sep)
    start = rootdir.rfind(os.sep) + 1
    for path, dirs, files in os.walk(rootdir):
        folders = path[start:].split(os.sep)
        # remove __init__.py
        if '__init__.py' in files: files.remove('__init__.py')
        # remove file extentions
        files_without_ext = [x[:-3] for x in files]
        # append all parents with dots to files: "folder.subfolder.file1"
        file_parent_pairs = []
        folders_without_root_dir = [x for x in folders if x != root_dir]
        print folders_without_root_dir
        for f in files_without_ext:
            file_with_parents = '.'.join(folders_without_root_dir + [f])
            file_parent_pairs.append((f, file_with_parents))

        subdir = dict.fromkeys(file_parent_pairs)
        parent = reduce(dict.get, folders[:-1], dir)
        parent[folders[-1]] = subdir
    dir = dir[root_dir]
    return dir


def get_page_objects(workspace, project):
    # find page objects directory

    page_objects_directory = ''
    #page_objects = []

    path = os.path.join(workspace, 'projects', project, 'pages')

    file_structure = {
        'name': '',
        'files': [],
        'childirs': {} }
        
    for root, dirs, files in os.walk(path):
        parents = root.replace(path, '').split(os.sep)
        parents.pop(0)
        current_directory = os.path.basename(root)
        files = [x[:-3] for x in files]
        if '__init__' in files: files.remove('__init__')

        this_dir_file_structure = {
                    'name': current_directory,
                    'files': files,
                    'childirs': {} }

        if len(parents) == 0:
            file_structure = this_dir_file_structure
        else:
            file_structure = go_one_level_deeper(
                                        file_structure, 
                                        this_dir_file_structure, 
                                        current_directory,
                                        parents)

    return file_structure



def new_directory(root_path, project, parents, directory_name):
    parents_joined = os.sep.join(parents)

    directory_path = os.path.join(
        root_path, 'projects', project, 'test_cases', parents_joined, directory_name)

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def new_directory_page_object(root_path, project, parents, directory_name):
    parents_joined = os.sep.join(parents)

    directory_path = os.path.join(
        root_path, 'projects', project, 'pages', parents_joined, directory_name)

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)






def run_test_case(project, test_case_name):
    os.system('python golem.py run {0} {1}'.format(project, test_case_name))




def get_time_span(task_id):

    path = os.path.join('results', '{0}.csv'.format(task_id))
    if not os.path.isfile(path):
        log_to_file('an error')
        return
    else: 
        with open(path, 'r') as f:
            reader = csv.DictReader(f, delimiter=';') 
            last_row = list(reader)[-1]
            exec_time = string_to_time(last_row['time'])
            time_delta = datetime.datetime.now() - exec_time
            total_seconds = time_delta.total_seconds()
            return total_seconds


def directory_already_exists(root_path, project, root_dir, parents, dir_name):
    parents_joined = os.sep.join(parents)

    directory_path = os.path.join(
        root_path, 'projects', project, root_dir, parents_joined, dir_name)    

    if os.path.exists(directory_path):
        return True
    else:
        return False

def log_to_file(string):
    print string


def time_to_string():
    time_format = '%Y-%m-%d-%H-%M-%S-%f'
    return datetime.datetime.now().strftime(time_format)

def string_to_time(time_string):
    return datetime.datetime.strptime(time_string, '%Y-%m-%d-%H-%M-%S-%f')


