import os
import json

from golem.core import utils


def get_envs(project):
    envs = []
    env_json_path = os.path.join('projects', project, 'environments.json')
    if os.path.exists(env_json_path):
        env_data = utils.load_json_from_file(env_json_path)
        envs = list(env_data.keys())
    return envs


def get_environment_data(project):
    env_data = {}
    env_json_path = os.path.join('projects', project, 'environments.json')
    if os.path.exists(env_json_path):
        env_data = utils.load_json_from_file(env_json_path)
    return env_data


def get_environments_as_string(project):
    env_data = ''
    env_json_path = os.path.join('projects', project, 'environments.json')
    if os.path.isfile(env_json_path):
        with open(env_json_path) as json_file:
            env_data = json_file.read()
    return env_data


def save_environments(project, env_data):
    error = ''
    if len(env_data):
        try:
            json.loads(env_data)
        except:
            error = 'must be valid JSON'
    if not error:
        environments_path = os.path.join('projects', project, 'environments.json')
        with open(environments_path, 'w') as env_file:
            env_file.write(env_data)
    return error
