import os

from golem.core import utils, session


def get_secrets(project):
    secrets_data = {}
    secrets_json_path = os.path.join(session.testdir, 'projects', project, 'secrets.json')
    if os.path.exists(secrets_json_path):
        json_data = utils.load_json_from_file(secrets_json_path, ignore_failure=True, default={})
        if json_data:
            secrets_data = json_data
    return secrets_data
