# _*_ coding: utf-8 _*_
"""
Time:     2023/3/21 19:51
Author:   不做评论(vvbbnn00)
Version:  
File:     password_utils.py
Describe: 
"""

import hashlib
import time
import uuid

from models import User, Token
from config import JWT_EXPIRATION_DELTA


def generate_salt():
    return uuid.uuid4().hex


def generate_password(password, salt):
    return hashlib.sha256(password.encode('utf-8') + salt.encode('utf-8')).hexdigest()


def verify_password(password, salt, hashed_password):
    return password == generate_password(hashed_password, salt)


def generate_token(user: User):
    token = Token(
        user=user,
        iss='server1',
        iat=time.time(),
        exp=time.time() + JWT_EXPIRATION_DELTA,
    )
    return token


def unpack_token(token):
    return Token.unpack(token)
