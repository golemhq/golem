import os, json


class User: 
    id = None
    username = None

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
        return unicode(self.id)  # python 2

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
                if user['password'] == password:
                    return True
                else:
                    return False
        return False


def get_user(user_id, root_path):
    with open(os.path.join(root_path, 'users.json')) as users_file:    
        user_data = json.load(users_file)
        for user in user_data:
            if user['id'] == user_id:
                new_user = User
                new_user.username = user['username']
                return new_user