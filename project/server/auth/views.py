# project/server/auth/views.py

from functools import wraps
from flask import g, Blueprint, request, make_response, jsonify
from flask.views import MethodView

from project.server import bcrypt, db
from project.server.models import User, BlacklistToken

auth_blueprint = Blueprint('auth', __name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # get the auth token
        auth_header = request.headers.get('Authorization')
        auth_token = auth_token = auth_header.split(" ")[1] if auth_header else ''
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                g.auth_token = auth_token
                g.user = User.query.filter_by(id=resp).first()
                return f(*args, **kwargs)
            response_object = {
                'status': 'fail',
                'message': resp
            }
            return make_response(jsonify(response_object)), 401
        else:
            response_object = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return make_response(jsonify(response_object)), 401
    return decorated_function


class RegisterAPI(MethodView):
    """
    User Registration Resource
    """

    def post(self):
        # get the post data
        post_data = request.get_json()
        # check if user already exists
        user = User.query.filter_by(email=post_data.get('email')).first()
        if not user:
            try:
                user = User(
                    email=post_data.get('email'),
                    password=post_data.get('password')
                )
                # insert the user
                db.session.add(user)
                db.session.commit()
                # generate the auth token
                auth_token = user.encode_auth_token(user.id)
                responseObject = {
                    'status': 'success',
                    'message': 'Successfully registered.',
                    'auth_token': auth_token.decode()
                }
                return make_response(jsonify(responseObject)), 201
            except Exception as e:
                responseObject = {
                    'status': 'fail',
                    'message': 'Some error occurred. Please try again.'
                }
                return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'User already exists. Please Log in.',
            }
            return make_response(jsonify(responseObject)), 202


class LoginAPI(MethodView):
    """
    User Login Resource
    """
    def post(self):
        # get the post data
        post_data = request.get_json()
        try:
            # fetch the user data
            user = User.query.filter_by(
                email=post_data.get('email')
            ).first()
            if user and bcrypt.check_password_hash(
                user.password, post_data.get('password')
            ):
                auth_token = user.encode_auth_token(user.id)
                if auth_token:
                    responseObject = {
                        'status': 'success',
                        'message': 'Successfully logged in.',
                        'auth_token': auth_token.decode()
                    }
                    return make_response(jsonify(responseObject)), 200
            else:
                responseObject = {
                    'status': 'fail',
                    'message': 'User does not exist.'
                }
                return make_response(jsonify(responseObject)), 404
        except Exception as e:
            print(e)
            responseObject = {
                'status': 'fail',
                'message': 'Try again'
            }
            return make_response(jsonify(responseObject)), 500


class UserAPI(MethodView):
    """
    User Resource
    """
    def get(self):
        responseObject = {
            'status': 'success',
            'data': {
                'user_id': g.user.id,
                'email': g.user.email,
                'admin': g.user.admin,
                'registered_on': g.user.registered_on
            }
        }
        return make_response(jsonify(responseObject)), 200


class LogoutAPI(MethodView):
    """
    Logout Resource
    """
    def post(self):
        # mark the token as blacklisted
        blacklist_token = BlacklistToken(token=g.auth_token)
        try:
            # insert the token
            db.session.add(blacklist_token)
            db.session.commit()
            responseObject = {
                'status': 'success',
                'message': 'Successfully logged out.'
            }
            return make_response(jsonify(responseObject)), 200
        except Exception as e:
            responseObject = {
                'status': 'fail',
                'message': e
            }
            return make_response(jsonify(responseObject)), 200

# define the API resources
registration_view = RegisterAPI.as_view('register_api')
login_view = LoginAPI.as_view('login_api')
user_view = UserAPI.as_view('user_api')
logout_view = LogoutAPI.as_view('logout_api')

# add Rules for API Endpoints
auth_blueprint.add_url_rule(
    '/auth/register',
    view_func=registration_view,
    methods=['POST']
)
auth_blueprint.add_url_rule(
    '/auth/login',
    view_func=login_view,
    methods=['POST']
)
auth_blueprint.add_url_rule(
    '/auth/status',
    view_func=login_required(user_view),
    methods=['GET']
)
auth_blueprint.add_url_rule(
    '/auth/logout',
    view_func=login_required(logout_view),
    methods=['POST']
)
