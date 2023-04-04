# _*_ coding: utf-8 _*_
"""
Time:     2023/4/4 18:55
Author:   不做评论(vvbbnn00)
Version:  
File:     __init__.py.py
Describe: 
"""
from datetime import timedelta

JWT_HASH_ALGORITHM = 'HS256'
JWT_EXPIRATION_DELTA = 86400
JWT_AUTH_HEADER_PREFIX = 'Bearer'
JWT_LEEWAY = 10
JWT_SECRET_KEY = '1@Riia001la--1ZZ..'

PASSWORD_PATTERN = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$'
USERNAME_PATTERN = r'^[a-zA-Z0-9_]{4,16}$'
EMAIL_PATTERN = r'^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$'
