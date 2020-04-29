"""Methods for dealing with GUI users."""
import json
import os
import uuid

from flask_login import current_user
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash

from golem.core import session, utils, test_directory


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
        with open(Users.file_path(), encoding='utf-8') as f:
            Users.set_users(json.load(f))

    @staticmethod
    def save():
        with open(Users.file_path(), 'w+', encoding='utf-8') as f:
            json.dump(Users.users(), f, indent=4, ensure_ascii=False)

    @staticmethod
    def users_file_exists():
        return os.path.isfile(Users.file_path())

    @staticmethod
    def create_users_file():
        with open(Users.file_path(), 'w', encoding='utf-8') as f:
            json.dump([], f)
        Users.refresh_users()

    @staticmethod
    def user_exists(username):
        return Users.get_user_by_username(username) is not None

    @staticmethod
    def generate_user_dictionary(id_, username, password, email, is_superuser, projects):
        user = {
            'id': id_,
            'username': username,
            'password': password,
            'email': email,
            'is_superuser': is_superuser,
            'projects': projects
        }
        return user

    @staticmethod
    def get_user_dictionary(username):
        if Users.user_exists(username):
            user = [u for u in Users.users() if u.get('username') == username][0]
            return Users.generate_user_dictionary(user['id'], user['username'],
                                                  user['password'], user['email'],
                                                  user['is_superuser'], user['projects'])
        else:
            return None

    @staticmethod
    def create_super_user(username, password, email=None):
        return Users.create_user(username, password, email, is_superuser=True)

    @staticmethod
    def create_user(username, password, email=None, is_superuser=False, projects=None):
        errors = []
        projects = projects or {}

        if not Users.users_file_exists():
            Users.create_users_file()

        username = username.strip()
        if len(username) == 0:
            errors.append('Username cannot be blank')
        elif Users.user_exists(username):
            errors.append('Username {} already exists'.format(username))

        if email is not None:
            email = email.strip()
            if len(email) == 0:
                email = None
            elif not utils.validate_email(email):
                errors.append('{} is not a valid email address'.format(email))

        if len(password) == 0:
            errors.append('Password cannot be blank')

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
        """Get a User object by id or username.
        Returns None if user is not found.
        Returns None if users.json format is invalid
        """
        user = None
        try:
            for u in Users.users():
                if id_ and u['id'] == id_:
                    user = u
                elif username and u['username'] == username:
                    user = u
            if user:
                user_obj = User(user['id'], user['username'], user['password'],
                                user['is_superuser'], user['email'], user['projects'])
                return user_obj
        except (KeyError, json.decoder.JSONDecodeError):
            print('Error: there was an error reading users.json file')
            import traceback
            traceback.print_exc()
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

    @staticmethod
    def add_project_to_user(username, project, permission):
        if Users.user_exists(username):
            for user in Users.users():
                if user['username'] == username:
                    user['projects'][project] = permission
                    Users.save()
                    return

    @staticmethod
    def delete_user(username):
        errors = []
        if not Users.user_exists(username):
            errors.append('Username {} does not exist'.format(username))
        elif current_user and current_user.is_authenticated and username == current_user.username:
            errors.append('Cannot delete current user')
        else:
            users = Users.users()
            users[:] = [u for u in users if u.get('username') != username]
            Users.set_users(users)
            Users.save()
        return errors

    @staticmethod
    def edit_user(username, new_username=None, new_email=False, new_is_superuser=None,
                  new_projects=None):
        errors = []
        if not Users.user_exists(username):
            errors.append('Username {} does not exist'.format(username))
        else:
            user = Users.get_user_dictionary(username)

            # Cannot remove superuser permissions if there is only one superuser
            superusers = [u for u in Users.users() if u['is_superuser']]
            if user['is_superuser'] and not new_is_superuser and len(superusers) == 1:
                errors.append('Cannot remove Superuser permission for this user')

            if new_username is not None and new_username != username:
                new_username = new_username.strip()
                if len(new_username) == 0:
                    errors.append('Username cannot be blank')
                elif Users.user_exists(new_username):
                    errors.append('Username {} already exists'.format(new_username))
                else:
                    user['username'] = new_username

            if type(new_email) is str or new_email is None:
                valid_email = False
                if type(new_email) is str:
                    new_email = new_email.strip()
                    if len(new_email) == 0:
                        new_email = None
                    elif utils.validate_email(new_email):
                        valid_email = True
                    else:
                        errors.append('{} is not a valid email address'.format(new_email))
                if (new_email is None or valid_email) and new_email != user['email']:
                    user['email'] = new_email

            if new_is_superuser is not None and new_is_superuser != user['is_superuser']:
                user['is_superuser'] = new_is_superuser

            if new_projects is not None and new_projects != user['projects']:
                user['projects'] = new_projects

            if not errors:
                users = Users.users()
                users[:] = [u for u in users if u.get('username') != username]
                users.append(user)
                Users.set_users(users)
                Users.save()
        return errors

    @staticmethod
    def reset_user_password(username, new_password):
        errors = []
        if not Users.user_exists(username):
            errors.append('Username {} does not exist'.format(username))
        else:
            if len(new_password) == 0:
                errors.append('Password cannot be blank')
            else:
                user = [u for u in Users.users() if u.get('username') == username][0]
                user['password'] = generate_password_hash(new_password)
                Users.save()
        return errors


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

    @property
    def project_list(self):
        projects = list(self.projects.keys())
        if self.is_superuser or '*' in projects:
            projects = test_directory.get_projects()
        return projects

    def project_permission(self, project):
        for p, permission in self.projects.items():
            if p == project:
                return permission
        return None

    def project_weight(self, project):
        if self.is_superuser:
            return Permissions.get_weight(Permissions.SUPER_USER)
        else:
            permission = self.project_permission(project)
            if permission:
                return Permissions.get_weight(permission)
        return 0

    def generate_auth_token(self, secret_key, expiration=600):
        s = Serializer(secret_key, expires_in=expiration)
        return s.dumps({'id': self.id})

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Permissions:

    SUPER_USER = 'super-user'
    ADMIN = 'admin'
    STANDARD = 'standard'
    READ_ONLY = 'read-only'
    REPORTS_ONLY = 'reports-only'

    weights = {
        SUPER_USER: 50,
        ADMIN: 40,
        STANDARD: 30,
        READ_ONLY: 20,
        REPORTS_ONLY: 10
    }

    project_permissions = [ADMIN, STANDARD, READ_ONLY, REPORTS_ONLY]

    @staticmethod
    def get_weight(permission):
        return Permissions.weights[permission]
