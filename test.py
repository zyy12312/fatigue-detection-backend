# _*_ coding: utf-8 _*_
"""
Time:     2023/4/11 18:08
Author:   不做评论(vvbbnn00)
Version:  
File:     test.py
Describe: 
"""
import utils.password_utils
from models import User

if __name__ == '__main__':
    user = User()
    user.username = 'vvbbnn00'
    user.salt = utils.password_utils.generate_salt()
    user.password = utils.password_utils.generate_password('123456', user.salt)
    user.save()
