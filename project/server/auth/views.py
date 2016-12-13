# project/server/auth/views.py

import codecs
import datetime
import json

import jwt
from flask import Blueprint, request, make_response, jsonify, current_app

from project.server import bcrypt, db
from project.server.models import User

auth_blueprint = Blueprint('auth', __name__,)


@auth_blueprint.route('/auth/register', methods=['POST'])
def register():
    post_data = request.get_json()
    # check if user already exists
    user = User.query.filter_by(email=post_data.get('email')).first()
    if not user:
        user = User(
            email=post_data.get('email'),
            password=post_data.get('password')
        )
        # insert the user
        db.session.add(user)
        db.session.commit()
        # generate token
        auth_token = generate_auth_token(user.id, user.email)
        responseObject = {
            'status': 'success',
            'message': 'Successfully registered.',
            'auth_token': auth_token.decode()
        }
        return make_response(jsonify(responseObject)), 201
    else:
        responseObject = {
            'status': 'fail',
            'message': 'User already exists. Please Login.'
        }
        return make_response(jsonify(responseObject)), 202


@auth_blueprint.route('/auth/login', methods=['POST'])
def login():
    post_data = request.get_json()
    user = User.query.filter_by(email=post_data.get('email')).first()
    if user and bcrypt.check_password_hash(
            user.password, post_data.get('password')):
        # generate token
        auth_token = generate_auth_token(user.id, user.email)
        responseObject = {
            'status': 'success',
            'message': 'Successfully logged in.',
            'auth_token': auth_token.decode()
        }
        return make_response(jsonify(responseObject)), 200
    else:
        responseObject = {
            'status': 'false',
            'message': 'User does not exist.'
        }
        return make_response(jsonify(responseObject)), 404


def generate_auth_token(user_id, email):
    return jwt.encode(
        {
            'user_id': user_id,
            'email': email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(
                days=0, seconds=5)
        },
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )
