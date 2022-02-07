import os
import json

from golem.core import utils, session


def get_envs(project):
    """get the list of envs defined in the environments.json file"""
    envs = []
    env_data = get_environment_data(project)
    if env_data:
        envs = list(env_data.keys())
    return envs


def get_environment_data(project):
    """get the full env data defined in the environments.json file"""
    env_data = {}
    env_path = environments_file_path(project)
    if os.path.isfile(env_path):
        json_data = utils.load_json_from_file(env_path, ignore_failure=True, default={})
        if json_data:
            env_data = json_data
    return env_data


def get_environments_as_string(project):
    """get the contents of environments.json file as string"""
    env_data = ''
    env_path = environments_file_path(project)
    if os.path.isfile(env_path):
        with open(env_path, encoding='utf-8') as f:
            env_data = f.read()
    return env_data


def save_environments(project, env_data):
    """save environments.json file contents.
    env_data must be a valid json string.
    Returns a string with the error or empty string otherwise"""
    error = ''
    if len(env_data):
        try:
            json.loads(env_data)
        except json.JSONDecodeError:
            error = 'must be valid JSON'
    if not error:
        env_path = environments_file_path(project)
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_data)
    return error


def environments_file_path(project):
    """Path to environments.json file"""
    return os.path.join(session.testdir, 'projects', project, 'environments.json')
