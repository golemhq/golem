import os
from distutils.version import LooseVersion

import golem
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
        f.write('secret_key = {}\n'.format(secret_key))


def is_valid_test_directory(testdir):
    """Verify `testdir` is a valid test directory path.
    It must contain a .golem file.
    This will only be checked for versions >= 0.9.0
    TODO
    """
    if LooseVersion(golem.__version__) >= LooseVersion('0.9.0'):
        if not os.path.isfile(os.path.join(testdir, '.golem')):
            return False
    return True
