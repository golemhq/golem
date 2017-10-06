import json
import os


class User:
    id = None
    username = None
    is_admin = False

    @property
    def is_authenticated(self):
        return True

    # @property
    # def is_admin(self):
    #     return self.is_admin

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User %r>' % (self.username)


def user_exists(username, root_path):
    with open(os.path.join(root_path, 'users.json')) as users_file:
        user_data = json.load(users_file)
        for user in user_data:
            if user['username'] == username:
                return user['id']
        return False


def password_is_correct(username, password, root_path):
    with open(os.path.join(root_path, 'users.json')) as users_file:
        user_data = json.load(users_file)
        for user in user_data:
            if user['username'] == username:
                return bool(user['password'] == password)
        return False


def get_user(user_id, root_path):
    with open(os.path.join(root_path, 'users.json')) as users_file:
        user_data = json.load(users_file)
        for user in user_data:
            if user['id'] == user_id:
                new_user = User
                new_user.username = user['username']
                new_user.id = user['id']
                new_user.is_admin = user['is_admin']
                return new_user


def has_permissions_to_project(user_id, project, root_path, module='gui'):
    with open(os.path.join(root_path, 'users.json')) as users_file:
        user_data = json.load(users_file)
        has_permission = False
        for user in user_data:
            if user['id'] == user_id:
                if module == 'gui':
                    project_in_projects = project in user['gui_projects']
                    asterisc_in_projects = '*' in user['gui_projects']
                elif module == 'report':
                    project_in_projects = project in user['report_projects']
                    asterisc_in_projects = '*' in user['report_projects']
                is_admin = user['is_admin']
                if project_in_projects or asterisc_in_projects or is_admin:
                    has_permission = True
        return has_permission


def is_admin(user_id, root_path):
    with open(os.path.join(root_path, 'users.json')) as users_file:
        user_data = json.load(users_file)
        for user in user_data:
            if user['id'] == user_id:
                return user['is_admin']
