# _*_ coding: utf-8 _*_
"""
Time:     2023/4/4 18:12
Author:   不做评论(vvbbnn00)
Version:  
File:     users.py
Describe: 
"""
import re

from flask_restx import Namespace, Resource
from . import APIBaseResponseSchema
from config import USERNAME_PATTERN, PASSWORD_PATTERN, EMAIL_PATTERN
from exceptions import UserAlreadyExistsException, BadRequestException
from .helpers.auth import need_login, has_role
from .helpers.request import validate_args
from service.users import *


class APIUserResponseSchema(APIBaseResponseSchema):
    username: str
    token: str
    expire: int = JWT_EXPIRATION_DELTA


class APIUserRequestSchema(object):
    username: str
    password: str


user_namespace = Namespace(path='/users', name='Users', description='Operations related to users')


@user_namespace.route('/login')
@user_namespace.doc(
    description='Login by username and password',
)
class Login(Resource):
    @validate_args({
        'username': (str, ...),
        'password': (str, ...),
    },
        location='json',
    )
    def post(self, data):
        username = data.get('username')
        password = data.get('password')
        user_data = login_by_username(username, password)
        token = generate_token(user_data)
        resp = APIUserResponseSchema(username=user_data.username,
                                     token=token.pack(),
                                     expire=token.exp)
        return {
            'code': 200,
            'message': 'ok',
            'data': resp.dict()
        }


@user_namespace.route('/user', methods=['POST', 'PUT', 'DELETE', 'GET'])
class UserInfo(Resource):

    @user_namespace.doc(description='Get user info by username or _id')
    @has_role('admin')
    @validate_args({
        'username': (str, None),
        'id': (str, None),
    },
        location='query',
    )
    def get(self, user, data):
        _id = data.get('id')
        username = data.get('username')
        if not _id and not username:
            return {
                'code': 400,
                'message': 'Bad Request',
                'errors': ["username or _id is required"]
            }
        if _id:
            user = User.find_by_id(_id)
        else:
            user = User.find_by_username(username)

        if not user:
            raise UserNotFoundException()

        del user.password
        del user.salt

        return {
            'code': 200,
            'message': 'ok',
            'data': user.dict()
        }

    @user_namespace.doc(description='Create a new user')
    @has_role('admin')
    @validate_args({
        'username': (str, ...),
        'password': (str, ...),
        'phone': (str, None),
        'email': (str, ...),
        'employee_id': (str, None),
        'name': (str, None),
        'college': (str, None),
        'roles': (list, None),
    }, location='json')
    def post(self, user, data):
        username = data.get('username')
        password = data.get('password')
        phone = data.get('phone')
        email = data.get('email')
        employee_id = data.get('employee_id')
        name = data.get('name')
        college = data.get('college')
        roles = data.get('roles')
        try:
            # [a-zA-Z0-9_]{4,16}$
            assert re.match(USERNAME_PATTERN, username), \
                'Username should be 4-16 characters, only letters, numbers and underscores are allowed'
            # ^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$
            assert re.match(PASSWORD_PATTERN, password), \
                'Password should be 8-16 characters, at least one uppercase letter, one lowercase letter and one number'
            assert re.match(EMAIL_PATTERN, email), 'Email is not valid'
        except AssertionError as e:
            raise BadRequestException(e.args[0])

        if User.find_by_username(username):
            raise UserAlreadyExistsException()

        salt = generate_salt()
        password = generate_password(password, salt)

        user = User(username=username,
                    password=password,
                    salt=salt,
                    phone=phone,
                    email=email,
                    employee_id=employee_id,
                    name=name,
                    college=college,
                    roles=roles)
        user.save()

        return {
            'code': 200,
            'message': 'ok',
            'data': user.dict()
        }

    @user_namespace.doc(description='Update user info')
    @has_role('admin')
    @validate_args({
        'id': (str, ...),
        'password': (str, None),
        'phone': (str, None),
        'email': (str, None),
        'employee_id': (str, None),
        'name': (str, None),
        'college': (str, None),
        'roles': (list, None),
    }, location='json')
    def put(self, user, data):
        _id = data.get('id')
        password = data.get('password')
        phone = data.get('phone')
        email = data.get('email')
        employee_id = data.get('employee_id')
        name = data.get('name')
        college = data.get('college')
        roles = data.get('roles')

        user = User.find_by_id(_id)

        if not user:
            raise UserNotFoundException()

        if password:
            if not re.match(PASSWORD_PATTERN, password):
                raise BadRequestException(
                    'Password should be 8-16 characters, at least one uppercase letter, '
                    'one lowercase letter and one number')
            user.password = password
        if phone:
            user.phone = phone
        if email:
            if not re.match(EMAIL_PATTERN, email):
                raise BadRequestException('Email is not valid')
            user.email = email
        if employee_id:
            user.employee_id = employee_id
        if name:
            user.name = name
        if college:
            user.college = college
        if roles:
            user.roles = roles

        user.save()

        return {
            'code': 200,
            'message': 'ok',
            'data': user.dict()
        }

    @user_namespace.doc(description='Delete user')
    @has_role('admin')
    @validate_args({
        'id': (str, ...),
    }, location='json')
    def delete(self, user, data):
        _id = data.get('id')
        user = User.find_by_id(_id)

        if not user:
            raise UserNotFoundException()

        user.delete()

        return {
            'code': 200,
            'message': 'ok',
            'data': {}
        }


@user_namespace.route('/list', methods=['GET'])
class UserList(Resource):
    @user_namespace.doc(description='Get user list')
    @has_role('admin')
    @validate_args({
        'page': (int, 1),
        'per_page': (int, 10),
        'username': (str, None),
        'phone': (str, None),
        'email': (str, None),
        'employee_id': (str, None),
        'name': (str, None),
        'college': (str, None),
        'roles': (str, None),
    }, location='query')
    def get(self, user, data):
        def filterUser(x):
            del x.password
            del x.salt
            return x.dict()

        page = data.get('page')
        if page < 1: page = 1
        per_page = data.get('per_page')
        if per_page < 1 or per_page > 100: per_page = 10
        username = data.get('username')
        phone = data.get('phone')
        email = data.get('email')
        employee_id = data.get('employee_id')
        name = data.get('name')
        college = data.get('college')
        roles = data.get('roles')

        query = {}
        if username:
            query['username'] = {'$regex': username}
        if phone:
            query['phone'] = {'$regex': phone}
        if email:
            query['email'] = {'$regex': email}
        if employee_id:
            query['employee_id'] = {'$regex': employee_id}
        if name:
            query['name'] = {'$regex': name}
        if college:
            query['college'] = {'$regex': college}
        if roles:
            query['roles'] = roles

        users = [filterUser(x) for x in User.query(query, per_page, (page - 1) * per_page)]

        return {
            'code': 200,
            'message': 'ok',
            'data': {
                'list': users,
                'total': len(users),
                'has_next': len(users) == per_page,
            }
        }


@user_namespace.route('/token', methods=['PUT'])
class Token(Resource):
    @user_namespace.doc(description='Get a new token')
    @need_login
    def put(self, user):
        token = generate_token(user)
        resp = APIUserResponseSchema(username=user.username,
                                     token=token.pack(),
                                     expire=token.exp)
        return {
            'code': 200,
            'message': 'ok',
            'data': resp.dict()
        }


@user_namespace.route('/me', methods=['GET'])
class Me(Resource):
    @user_namespace.doc(description='Get current user info')
    @has_role('admin')
    def get(self, user):
        del user.password
        del user.salt

        return {
            'code': 200,
            'message': 'ok',
            'data': user.dict()
        }
