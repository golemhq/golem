import random
import os
import string
from subprocess import call


def create_project(workspace, name):
    os.chdir(workspace)
    call(['python', 'golem.py', 'createproject', name])


def create_random_project(workspace):
    random_value = ''.join(random.choice(string.ascii_lowercase) for _ in range(4))
    random_name = 'project_' + random_value
    create_project(workspace, random_name)
    return random_name
