from flask_login import UserMixin
# User class represents one user of our website
# UserMixin automatically adds methods like:
# get_id(), is_authenticated, is_active, etc.
class User(UserMixin):
    # Constructor runs whenever we create a new User object
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email