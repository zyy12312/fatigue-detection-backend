# _*_ coding: utf-8 _*_
"""
Time:     2023/4/4 19:30
Author:   不做评论(vvbbnn00)
Version:  
File:     auth.py
Describe: 
"""
from functools import wraps

from flask import request
from exceptions import TokenInvalidError, ForbiddenException
from config import JWT_AUTH_HEADER_PREFIX
from models import User
from service.users import get_user_from_token


def need_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            raise TokenInvalidError("unauthorized")
        if not token.startswith(JWT_AUTH_HEADER_PREFIX + ' '):
            raise TokenInvalidError("invalid token")
        token = token[len(JWT_AUTH_HEADER_PREFIX) + 1:]
        user = get_user_from_token(token)
        return func(*args, user, **kwargs)

    return wrapper


def has_role(role: str or list):
    def decorator(func):
        @wraps(func)
        @need_login
        def wrapper(*args, **kwargs):
            user = None
            for arg in args:
                if isinstance(arg, User):
                    user = arg
                    break
            if not user:
                raise TokenInvalidError("unauthorized")
            if isinstance(role, str) and role not in user.roles:
                raise ForbiddenException()
            if isinstance(role, list) and not set(role).intersection(set(user.roles)):
                raise ForbiddenException()
            return func(*args, **kwargs)

        return wrapper

    return decorator
