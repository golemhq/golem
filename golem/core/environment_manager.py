import os
import json


def get_envs(project):
    envs = []
    env_json_path = os.path.join('projects', project, 'environments.json')
    if os.path.exists(env_json_path):
        with open(env_json_path) as json_file:
            env_data = json.load(json_file)
            envs = list(env_data.keys())
    return envs


def get_environment_data(project):
    env_data = {}
    env_json_path = os.path.join('projects', project, 'environments.json')
    if os.path.exists(env_json_path):
        with open(env_json_path) as json_file:
            env_data = json.load(json_file)
    return env_data


def get_environments_as_string(project):
    env_data = ''
    env_json_path = os.path.join('projects', project, 'environments.json')
    if os.path.isfile(env_json_path):
        with open(env_json_path) as json_file:
            env_data = json_file.read()
    return env_data


def save_environments(project, env_data):
    environments_path = os.path.join('projects', project, 'environments.json')
    with open(environments_path, 'w') as env_file:
        env_file.write(env_data)
    return