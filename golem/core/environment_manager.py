import os
import json

from golem.core import utils


def get_envs(workspace, project):
    """get the list of envs defined in the environments.json file"""
    envs = []
    env_data = get_environment_data(workspace, project)
    if env_data:
        envs = list(env_data.keys())
    return envs


def get_environment_data(workspace, project):
    """get the full env data defined in the environments.json file"""
    env_data = {}
    env_json_path = os.path.join(workspace, 'projects', project, 'environments.json')
    if os.path.exists(env_json_path):
        json_data = utils.load_json_from_file(env_json_path,
                                              ignore_failure=True,
                                              default={})
        if json_data:
            env_data = json_data
    return env_data


def get_environments_as_string(workspace, project):
    """get the contents of environments.json file as string"""
    env_data = ''
    env_json_path = os.path.join(workspace, 'projects', project, 'environments.json')
    if os.path.isfile(env_json_path):
        with open(env_json_path) as json_file:
            env_data = json_file.read()
    return env_data


def save_environments(workspace, project, env_data):
    """save environments.json file contents.
    env_data must be a valid json string.
    Returns a string with the error or empty string otherwise"""
    error = ''
    if len(env_data):
        try:
            json.loads(env_data)
        except:
            error = 'must be valid JSON'
    if not error:
        environments_path = os.path.join(workspace, 'projects', project, 'environments.json')
        with open(environments_path, 'w') as env_file:
            env_file.write(env_data)
    return error
