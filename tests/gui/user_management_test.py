import json
import os
import time

import pytest
from itsdangerous import BadSignature, SignatureExpired

from golem.gui import create_app
from golem.gui.user_management import Users, Permissions


class TestUsers:

    @pytest.mark.slow
    def test_users(self, testdir_function, test_utils):
        testdir_function.activate()
        users = Users.users()
        assert len(users) == 1
        username = test_utils.random_string(10)
        Users.create_user(username, '123')
        users = Users.users()
        assert len(users) == 2
        assert Users.user_exists(username)

    def test_refresh_users(self, testdir_function):
        testdir_function.activate()
        user1 = Users.generate_user_dictionary('01', 'username01', '123', None, True, [])
        user2 = Users.generate_user_dictionary('02', 'username02', '123', None, True, [])
        assert len(Users.users()) == 1
        with open(Users.file_path(), 'w') as f:
            json.dump([user1, user2], f)
        Users.refresh_users()
        assert len(Users.users()) == 2

    def test_create_users_file(self, testdir_function):
        testdir_function.activate()
        os.remove(Users.file_path())
        Users.create_users_file()
        assert os.path.isfile(Users.file_path())
        with open(Users.file_path()) as f:
            assert f.read() == '[]'
        assert Users.users() == []

    def test_user_exists(self, testdir_function):
        testdir_function.activate()
        assert Users.user_exists('admin')
        assert not Users.user_exists('not-exist')

    def test_create_super_user(self, testdir_function, test_utils):
        testdir_function.activate()
        username = test_utils.random_string(10)
        Users.create_super_user(username, '123456')
        user = Users.get_user_by_username(username)
        assert user.is_superuser

    def test_create_user_file(self, testdir_class):
        testdir_class.activate()

    def test_create_user_file_not_exist(self, testdir_function, test_utils):
        """Users file is created if it does not exist"""
        testdir_function.activate()
        username = test_utils.random_string(5)
        os.remove(Users.file_path())
        Users.create_user(username, '123', None)
        assert os.path.isfile(Users.file_path())
        assert Users.user_exists(username)

    def test_create_user_blank_username(self, testdir_class):
        testdir_class.activate()
        errors = Users.create_user('', '123', None)
        assert errors == ['Username cannot be blank']

    def test_create_user_user_exists(self, testdir_class, test_utils):
        testdir_class.activate()
        username = test_utils.random_string(5)
        Users.create_user(username, '123', None)
        errors = Users.create_user(username, '123', None)
        assert errors == ['Username {} already exists'.format(username)]

    def test_create_user_invalid_email(self, testdir_class, test_utils):
        testdir_class.activate()
        username = test_utils.random_string(5)
        email = 'test@'
        errors = Users.create_user(username, '123', email)
        assert errors == ['{} is not a valid email address'.format(email)]

    def test_create_user_empty_password(self, testdir_class, test_utils):
        testdir_class.activate()
        username = test_utils.random_string(5)
        errors = Users.create_user(username, '')
        assert errors == ['Password cannot be blank']

    def test_create_user_password_is_hashed(self, testdir_class, test_utils):
        testdir_class.activate()
        username = test_utils.random_string(5)
        password = '123456'
        Users.create_user(username, password)
        assert Users.get_user_by_username(username).password != password

    def test_verify_auth_token(self, testdir_class, test_utils):
        testdir_class.activate()
        username = test_utils.random_string(5)
        password = '123456'
        Users.create_user(username, password)
        app = create_app()
        token = Users.get_user_by_username(username).generate_auth_token(app.secret_key)
        user = Users.verify_auth_token(app.secret_key, token)
        assert user.username == username

    def test_verify_auth_token_invalid_token(self, testdir_class, test_utils):
        testdir_class.activate()
        username = test_utils.random_string(5)
        password = '123456'
        Users.create_user(username, password)
        app = create_app()
        with pytest.raises(BadSignature) as _:
            Users.verify_auth_token(app.secret_key, 'invalid_token')

    @pytest.mark.slow
    def test_verify_auth_token_expired_token(self, testdir_class, test_utils):
        testdir_class.activate()
        username = test_utils.random_string(5)
        password = '123456'
        Users.create_user(username, password)
        app = create_app()
        user = Users.get_user_by_username(username)
        token = user.generate_auth_token(app.secret_key, expiration=1)
        time.sleep(2)
        with pytest.raises(SignatureExpired):
            Users.verify_auth_token(app.secret_key, token)

    @pytest.mark.slow
    def test_verify_password(self, testdir_class, test_utils):
        testdir_class.activate()
        username = test_utils.random_string(5)
        password = '123456'
        Users.create_user(username, password)
        assert Users.verify_password(username, password)
        assert not Users.verify_password(username, 'invalid_password')

    def test_add_project_to_user(self, project_function_clean, test_utils):
        testdir, project = project_function_clean.activate()
        username = test_utils.random_string(5)
        Users.create_user(username, '123456')
        Users.add_project_to_user(username, project, Permissions.SUPER_USER)
        user = Users.get_user_by_username(username)
        assert project in user.projects
        assert user.projects[project] == Permissions.SUPER_USER

    def test_delete_user(self, testdir_class, test_utils):
        testdir_class.activate()
        username = test_utils.random_string(5)
        Users.create_user(username, '123456')
        errors = Users.delete_user(username)
        assert errors == []
        assert not Users.user_exists(username)

    def test_delete_user_not_exist(self, testdir_class):
        testdir_class.activate()
        username = 'username01'
        errors = Users.delete_user(username)
        assert errors == ['Username {} does not exist'.format(username)]

    def test_edit_user(self, testdir_class, test_utils):
        testdir_class.activate()
        username = test_utils.random_string(5)
        email = test_utils.random_email()
        Users.create_user(username, '123456', email)
        new_username = test_utils.random_string(5)
        new_email = test_utils.random_email()
        errors = Users.edit_user(username, new_username, new_email)
        assert errors == []
        user = Users.get_user_by_username(new_username)
        assert user.email == new_email

    def test_edit_user_not_exist(self, testdir_class):
        testdir_class.activate()
        errors = Users.edit_user('username', 'new_username')
        assert errors == ['Username username does not exist']

    def test_edit_user_remove_all_superuser_permissions(self, testdir_function):
        """Cannot edit a user and remove superuser permissions if it's
        the only superuser available
        """
        testdir_function.activate()
        assert len(Users.users()) == 1
        Users.create_user('standard', '123456')
        assert len(Users.users()) == 2
        errors = Users.edit_user('admin', new_is_superuser=False)
        assert errors == ['Cannot remove Superuser permission for this user']

    def test_edit_user_username_blank(self, testdir_class, test_utils):
        testdir_class.activate()
        username = test_utils.random_string(5)
        email = test_utils.random_email()
        Users.create_user(username, '123456', email)
        errors = Users.edit_user(username, new_username='')
        assert errors == ['Username cannot be blank']

    def test_edit_user_new_username_exists(self, testdir_class, test_utils):
        testdir_class.activate()
        username = test_utils.random_string(5)
        Users.create_user(username, '123456')
        new_username = test_utils.random_string(5)
        Users.create_user(new_username, '123456')
        errors = Users.edit_user(username, new_username=new_username)
        assert errors == ['Username {} already exists'.format(new_username)]

    def test_edit_user_email(self, testdir_class, test_utils):
        testdir_class.activate()
        username = test_utils.random_string(5)
        email = test_utils.random_email()
        Users.create_user(username, '123456', email)
        # Do not edit user email
        Users.edit_user(username, new_email=False)
        assert Users.get_user_by_username(username).email == email
        # '' is converted to None
        Users.edit_user(username, new_email='')
        assert Users.get_user_by_username(username).email is None
        Users.edit_user(username, new_email=email)
        assert Users.get_user_by_username(username).email == email
        # Email is saved as None
        Users.edit_user(username, new_email=None)
        assert Users.get_user_by_username(username).email is None

    def test_edit_user_invalid_email(self, testdir_class, test_utils):
        testdir_class.activate()
        username = test_utils.random_string(5)
        email = test_utils.random_email()
        Users.create_user(username, '123456', email)
        new_email = 'test@'
        errors = Users.edit_user(username, new_email=new_email)
        assert errors == ['{} is not a valid email address'.format(new_email)]

    @pytest.mark.slow
    def test_reset_user_password(self, testdir_class, test_utils):
        testdir_class.activate()
        username = test_utils.random_string(5)
        Users.create_user(username, '123456')
        hashed_password = Users.get_user_by_username(username).password
        errors = Users.reset_user_password(username, '234567')
        assert errors == []
        new_hashed_password = Users.get_user_by_username(username).password
        assert hashed_password != new_hashed_password

    def test_reset_user_password_user_not_exist(self, testdir_class, test_utils):
        testdir_class.activate()
        username = test_utils.random_string(5)
        errors = Users.reset_user_password(username, '234567')
        assert errors == ['Username {} does not exist'.format(username)]

    def test_reset_user_password_blank(self, testdir_class, test_utils):
        testdir_class.activate()
        username = test_utils.random_string(5)
        Users.create_user(username, '123456')
        errors = Users.reset_user_password(username, '')
        assert errors == ['Password cannot be blank']


class TestUser:

    @pytest.mark.slow
    def test_verify_password(self, testdir_class, test_utils):
        testdir_class.activate()
        username = test_utils.random_string(5)
        password = '123456'
        Users.create_user(username, password)
        user = Users.get_user_by_username(username)
        assert user.password != password
        assert user.verify_password(password)
        assert not user.verify_password('invalid_password')

    def test_project_weight(self, project_class, test_utils):
        testdir, project = project_class.activate()
        username = test_utils.random_string(5)
        Users.create_user(username, '123456')
        Users.add_project_to_user(username, project, Permissions.ADMIN)
        user = Users.get_user_by_username(username)
        assert user.project_weight(project) == Permissions.weights[Permissions.ADMIN]


class TestPermissions:

    def test_get_weight(self):
        assert Permissions.get_weight(Permissions.SUPER_USER) == 50
        assert Permissions.get_weight(Permissions.ADMIN) == 40
        assert Permissions.get_weight(Permissions.STANDARD) == 30
        assert Permissions.get_weight(Permissions.READ_ONLY) == 20
        assert Permissions.get_weight(Permissions.REPORTS_ONLY) == 10
