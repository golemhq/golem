"""Methods for dealing with GUI users."""
import json
import os
import uuid

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash

from golem.core import session, utils


class Users:

    _users = None

    @staticmethod
    def file_path():
        return os.path.join(session.testdir, 'users.json')

    @staticmethod
    def users():
        if not Users._users:
            Users.refresh_users()
        return Users._users

    @staticmethod
    def set_users(users):
        Users._users = users

    @staticmethod
    def refresh_users():
        with open(Users.file_path()) as f:
            Users.set_users(json.load(f))

    @staticmethod
    def save():
        with open(Users.file_path(), 'w+') as f:
            json.dump(Users.users(), f, indent=4)

    @staticmethod
    def users_file_exists():
        return os.path.isfile(Users.file_path())

    @staticmethod
    def create_users_file():
        with open(Users.file_path(), 'w') as f:
            json.dump([], f)
        Users.refresh_users()

    @staticmethod
    def user_exists(username):
        return any(user['username'] == username for user in Users.users())

    @staticmethod
    def generate_user_dictionary(id_, username, password, email, is_superuser, projects):
        new_user = {
            'id': id_,
            'username': username,
            'password': password,
            'email': email,
            'is_superuser': is_superuser,
            'projects': projects
        }
        return new_user

    @staticmethod
    def create_super_user(username, password, email=None):
        return Users.create_user(username, password, email, is_superuser=True)

    @staticmethod
    def create_user(username, password, email=None, is_superuser=False, projects=None):
        errors = []

        if not Users.users_file_exists():
            Users.create_users_file()

        username = username.strip()
        if len(username) == 0:
            errors.append('username cannot be blank')
        elif Users.user_exists(username):
            errors.append('username {} already exists'.format(username))

        if email is not None:
            email = email.strip()
            if len(email) == 0:
                email = None
            elif not utils.validate_email(email):
                errors.append('{} is not a valid email address'.format(email))

        if len(password) == 0:
            errors.append('password cannot be blank')

        if not errors:
            id_ = str(uuid.uuid4())[:8]
            hashed_password = generate_password_hash(password)
            user = Users.generate_user_dictionary(id_, username, hashed_password, email,
                                                  is_superuser, projects)
            Users.users().append(user)
            Users.save()
        return errors

    @staticmethod
    def get_user_by_id(id_):
        return Users._get_user(id_=id_)

    @staticmethod
    def get_user_by_username(username):
        return Users._get_user(username=username)

    @staticmethod
    def _get_user(id_=None, username=None):
        user = None
        for u in Users.users():
            if id_ and u['id'] == id_:
                user = u
            elif username and u['username'] == username:
                user = u
        if user:
            user_obj = User(user['id'], user['username'], user['password'],
                            user['is_superuser'], user['email'], user['projects'])
            return user_obj
        else:
            return None

    @staticmethod
    def verify_auth_token(secret_key, token):
        """Verify token is valid.

        :Returns:
          The user

        :Raises:
         - itsdangerous.BadSignature: token is invalid
         - itsdangerous.SignatureExpired: token has expired
        """
        s = Serializer(secret_key)
        data = s.loads(token)
        return Users.get_user_by_id(data['id'])

    @staticmethod
    def verify_password(username, password):
        user = Users.get_user_by_username(username)
        return user.verify_password(password)


class User:

    def __init__(self, id_, username, password, is_superuser=False, email=None, projects=None):
        self.id = id_
        self.username = username
        self.email = email
        self.password = password
        self.is_superuser = is_superuser
        self.projects = projects

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

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def has_gui_permissions(self, project):
        # return (project in self.gui_permissions or
        #         '*' in self.gui_permissions or
        #         self.is_admin)
        return True

    def has_report_permissions(self, project):
        # return (project in self.report_permissions or
        #         '*' in self.report_permissions or
        #         self.is_admin)
        return True

    def generate_auth_token(self, secret_key, expiration=600):
        s = Serializer(secret_key, expires_in=expiration)
        return s.dumps({'id': self.id})

    def __repr__(self):
        return '<User {}>'.format(self.username)
