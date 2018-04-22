import random
import os
import string
from subprocess import call
import subprocess


def random_string(length, prefix=''):
	random_str = ''.join(random.choice(string.ascii_lowercase) for _ in range(length))
	return prefix + random_str


def create_project(workspace, name):
    os.chdir(workspace)
    call(['golem', 'createproject', name])


def create_random_project(workspace):
    random_name = random_string(4, 'project_')
    create_project(workspace, random_name)
    return random_name


def run_command(cmd):
    output = ''
    p = subprocess.Popen(cmd,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    for line in iter(p.stdout.readline, b''):
        line_parsed = line.decode('ascii').replace('\r', '')
        output += line_parsed

    if len(output) > 1 and output[-1] == '\n':
        output = output[:-1]
    return output