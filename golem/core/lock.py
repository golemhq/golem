import os
import random
from datetime import datetime

from golem.core import utils


max_time_delta_seconds = 60


def random_cleanup(workspace, project):
    if random.randrange(50) == 1:
        path = os.path.join(workspace, 'projects', project, 'lock')
        lines = []
        cleaned_lines = []
        with open(path) as file:
            lines = file.readlines()
        for line in lines:
            split_line = line.split(' ')
            date = utils.get_date_from_timestamp(split_line[1])
            delta = datetime.now() - date
            if delta.seconds <= max_time_delta_seconds * 3:
                cleaned_lines.append(line)
        with open(path, 'w') as file:
            for line in cleaned_lines:
                file.write(line)


def is_file_locked(workspace, project, file_name):
    path = os.path.join(workspace, 'projects', project, 'lock')
    lines = []
    if os.path.exists(path):
        with open(path) as file:
            lines = file.readlines()
        for line in lines:
            split_line = line.split(' ')
            if split_line[0] == file_name:
                date = utils.get_date_from_timestamp(split_line[1])
                delta = datetime.now() - date
                if delta.seconds <= max_time_delta_seconds:
                    return split_line[3].replace('\n', '')
    else:
        open(path, 'a').close()

    return False


def lock_file(workspace, project, file_name, username):
    timestamp = utils.get_timestamp()
    path = os.path.join(workspace, 'projects', project, 'lock')
    with open(path, 'a') as file:
        file.write('{0} {1} by {2}'.format(file_name, timestamp, username))
    random_cleanup(workspace, project)


def unlock_file(workspace, project, file_name, username):
    path = os.path.join(workspace, 'projects', project, 'lock')
    lines = []
    cleaned_lines = []
    with open(path) as file:
        lines = file.readlines()
    for line in lines:
        split_line = line.split(' ')
        if split_line[0] != file_name and split_line[2].replace('\n', '') != username:
            cleaned_lines.append(line)
    with open(path, 'w') as file:
        for line in cleaned_lines:
            file.write(line)
