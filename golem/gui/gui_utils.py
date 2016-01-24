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


def go_one_level_deeper(file_structure, this_dir_file_structure, current_directory, parents):
    first_parent = parents[0]
    parents.pop(0)
    if len(parents) == 0:

        file_structure['childirs'][current_directory] = this_dir_file_structure
    else: 
        file_structure['childirs'][first_parent] = go_one_level_deeper(
                                    file_structure['childirs'][first_parent],
                                    this_dir_file_structure,
                                    current_directory,
                                    parents)
    return file_structure


def get_test_cases(workspace, project):
    path = os.path.join(workspace, 'projects', project, 'test_cases')

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



def get_page_objects(workspace, project):
    # find page objects directory

<<<<<<< HEAD
    page_objects_directory = ''
=======
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



def get_page_objects__DEPRECADO(workspace, project):
    # find page objects directory

>>>>>>> 5b0994a4f56709128e23d78d2a054e42a8c0105e
    page_objects = []

    path = os.path.join(workspace, 'projects', project, 'pages')

<<<<<<< HEAD
=======
    file_structure = {
        'name': '',
        'files': [],
        'childirs': {} }

>>>>>>> 5b0994a4f56709128e23d78d2a054e42a8c0105e
    for root, dirs, files in os.walk(path):
        current_directory = os.path.basename(root)
        for f in files:
            if not f == '__init__.py':
                page_objects.append({
                    'name': f[:-3],
                    'path': root})

    return page_objects






def new_directory(root_path, project, directory_name):
    directory_path = os.path.join(
        root_path, 'projects', project, 'test_cases', directory_name)

    print directory_path
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



def log_to_file(string):
    print string


def time_to_string():
    time_format = '%Y-%m-%d-%H-%M-%S-%f'
    return datetime.datetime.now().strftime(time_format)

def string_to_time(time_string):
    return datetime.datetime.strptime(time_string, '%Y-%m-%d-%H-%M-%S-%f')


