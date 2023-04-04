# _*_ coding: utf-8 _*_
"""
Time:     2023/4/4 18:43
Author:   不做评论(vvbbnn00)
Version:  
File:     users.py
Describe: 
"""
from exceptions import UserNotFoundException, UserPasswordNotMatchException
from models import User
from utils.password_utils import *


def login_by_username(username, password):
    user = User.find_by_username(username)
    if not user:
        raise UserNotFoundException()
    if not verify_password(user.password, user.salt, password):
        raise UserPasswordNotMatchException()
    return user


def get_user_from_token(token):
    user_dict = Token.unpack(token)
    user = User.find_by_id(user_dict.user._id)

    if not user:
        raise UserNotFoundException()
    return user
