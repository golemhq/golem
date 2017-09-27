import sys
import os

from golem.core import utils


def log_change(workspace, project, action, file_type, file_name, username):
    valid_actions = ['CREATE', 'MODIFY', 'RUN']
    valid_file_types = ['test']
    if action not in valid_actions:
        sys.exit('ERROR: {} is not a valid changelog action'.format(action))
    if file_type not in valid_file_types:
        sys.exit('ERROR: {} is not a valid file type'.format(file_type))
    timestamp = utils.get_timestamp()
    path = os.path.join(workspace, 'projects', project, 'changelog')
    with open(path, 'a+') as file:
        file.write('{0} {1} {2} {3} by {4}\n'.format(timestamp, action, file_type,
                                                     file_name, username))
        