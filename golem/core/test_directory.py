import os

import webdriver_manager

from golem.core import file_manager, settings_manager, session
from golem.gui.user_management import Users


def create_test_directory(testdir):
    file_manager.create_directory(path_list=[testdir], add_init=True)
    file_manager.create_directory(path_list=[testdir, 'projects'], add_init=True)
    file_manager.create_directory(path_list=[testdir, 'drivers'], add_init=False)
    settings_manager.create_global_settings_file(testdir)
    create_testdir_golem_file(testdir)
    session.testdir = testdir
    Users.create_super_user('admin', 'admin')


def create_testdir_golem_file(testdir):
    """Create .golem file"""
    golem_file = os.path.join(testdir, '.golem')
    with open(golem_file, 'w') as f:
        secret_key = os.urandom(24).hex()
        f.write('[gui]\n')
        f.write(f'secret_key = {secret_key}\n')


def get_projects():
    path = os.path.join(session.testdir, 'projects')
    projects = next(os.walk(path))[1]
    projects = [x for x in projects if x != '__pycache__']
    return projects


def project_exists(project):
    return project in get_projects()


def is_valid_test_directory(testdir):
    """Verify `testdir` is a valid test directory path.
    It must contain a .golem file.
    """
    return os.path.isfile(os.path.join(testdir, '.golem'))


def drivers_path():
    return os.path.join(session.testdir, 'drivers')


# def get_driver_versions():
#     return webdriver_manager.versions(drivers_path())


def get_driver_folder_files():
    """Get the list of files in testdir/drivers folder.
    Folders are ignored. TODO
    """
    files = []
    path = drivers_path()
    lst = os.listdir(path)
    for elem in lst:
        if os.path.isfile(os.path.join(path, elem)):
            files.append(elem)
    return files


def delete_driver_file(filename):
    errors = []
    path = os.path.join(drivers_path(), filename)
    if not os.path.isfile(path):
        errors.append(f'File {filename} does not exist')
    else:
        try:
            os.remove(path)
        except Exception as e:
            errors.append(f'There was an error removing file {filename}')
    return errors


def update_driver(driver_name):
    if driver_name not in ['chromedriver', 'geckodriver']:
        return f'{driver_name} is not a valid driver name'
    webdriver_manager.update(driver_name, drivers_path())
    return ''  # TODO: webdriver-manager should return actual error messages
