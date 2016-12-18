# project/server/models.py


import datetime
import jwt

from project.server import app, db, bcrypt


class User(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, email, password, admin=False):
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, app.config.get('BCRYPT_LOG_ROUNDS')
        )
        self.registered_on = datetime.datetime.now()
        self.admin = admin

    def generate_auth_token(self, id, email):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            return jwt.encode(
                {
                    'user_id': id,
                    'email': email,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=5)
                },
                app.config.get('JWT_SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def validate_auth_token(auth_token):
        """
        Validates the auth token
        :param auth_token:
        :return: boolean|string
        """
        # check whether auth token has been blacklisted
        blacklist_token = BlacklistToken.query.filter_by(token=auth_token).first()
        if blacklist_token:
            return 'Invalid token. Please login again.'

        # non-blacklisted token validation
        try:
            payload = jwt.decode(auth_token, app.config.get('JWT_SECRET_KEY'))
            user = User.query.filter_by(id=payload['user_id'], email=payload['email']).first()
            return user
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'

    def is_authenticated(self):
        """ Tells whether user is authenticated or not """
        return True

    def is_active(self):
        """ Tells whether user is active or not """
        return True

    def is_anonymous(self):
        """ Tells whether user is anonymous or not """
        return False

    def get_id(self):
        """ Returns id for the current user """
        return self.id

    def __repr__(self):
        return '<User {0}>'.format(self.email)


class BlacklistToken(db.Model):
    """
    Token Model for storing JWT tokens
    """
    __tablename__ = 'blacklist_tokens'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    def __repr__(self):
        return '<id: token: {}'.format(self.token)
