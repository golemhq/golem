import os
import json

from golem.core import secrets_manager

SECRETS = {
    "db_host": "db-server-01.local",
    "schema": "public",
    "users": {
        "user01": "Mike"
    }
}


class TestGetSecrets:

    def test_get_secrets_in_case_secrets_file_does_not_exists(self, project_session):
        testdir = project_session.testdir
        project = project_session.name
        secrets = secrets_manager.get_secrets(testdir, project)

        assert len(secrets) == 0
        assert {} == secrets

    def test_get_secrets_in_case_secrets_file_exists(self, project_session):
        testdir = project_session.testdir
        project = project_session.name
        secrets_path = os.path.join(project_session.path, 'secrets.json')
        with open(secrets_path, 'w') as secrets_file:
            secrets_file.write(json.dumps(SECRETS, indent=True))
        secrets = secrets_manager.get_secrets(testdir, project)

        assert len(secrets) == 3
        assert 'db_host' in secrets
        assert 'schema' in secrets
        assert 'Mike' == secrets['users']['user01']
