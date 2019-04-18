"""Methods for dealing with GUI users."""
import json
import os

from golem.core import session


def get_user_data(username=None, id_=None):
    if not username and not id_:
        raise ValueError('either username or id is required')
    user_data = None
    with open(os.path.join(session.testdir, 'users.json')) as f:
        users_data = json.load(f)
        for user in users_data:
            if username and user['username'] == username:
                user_data = user
            if id_ and user['id'] == id_:
                user_data = user
    return user_data


def get_user_from_id(id_):
    user_data = get_user_data(id_=id_)
    user_ = None
    if user_data:
        user_ = User(user_data['id'], user_data['username'], user_data['is_admin'],
                     user_data['gui_projects'], user_data['report_projects'])
    return user_


class User:

    def __init__(self, id_, username, is_admin, gui_projects, report_projects):
        self.id = id_
        self.username = username
        self.is_admin = is_admin
        self.gui_permissions = gui_projects
        self.report_permissions = report_projects

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def has_gui_permissions(self, project):
        return (project in self.gui_permissions or
                '*' in self.gui_permissions or
                self.is_admin)

    def has_report_permissions(self, project):
        return (project in self.report_permissions or
                '*' in self.report_permissions or
                self.is_admin)

    def __repr__(self):
        return '<User {}>'.format(self.username)
