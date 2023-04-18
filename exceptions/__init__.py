# _*_ coding: utf-8 _*_
"""
Time:     2023/4/4 18:44
Author:   不做评论(vvbbnn00)
Version:  
File:     __init__.py.py
Describe: 
"""


class BaseServiceException(Exception):
    def __init__(self, message, code=500):
        self.message = message
        self.code = code

    def __str__(self):
        return self.message


class UserNotFoundException(BaseServiceException):
    def __init__(self, message='User not found', code=404):
        super().__init__(message, code)


class UserPasswordNotMatchException(BaseServiceException):
    def __init__(self, message='Incorrect username or password.', code=400):
        super().__init__(message, code)


class UserAlreadyExistsException(BaseServiceException):
    def __init__(self, message='User already exists', code=400):
        super().__init__(message, code)


class UserNotLoginException(BaseServiceException):
    def __init__(self, message='Unauthorized', code=401):
        super().__init__(message, code)


class TokenInvalidError(BaseServiceException):
    def __init__(self, message='Token invalid', code=401):
        super().__init__(message, code)


class ForbiddenException(BaseServiceException):
    def __init__(self, message='You don\'t have the permission to do that.', code=403):
        super().__init__(message, code)


class BadRequestException(BaseServiceException):
    def __init__(self, message='Bad request', code=400):
        super().__init__(message, code)


class CourseNotFoundException(BaseServiceException):
    def __init__(self, message='Course not found', code=404):
        super().__init__(message, code)


class CourseAlreadyExistsException(BaseServiceException):
    def __init__(self, message='Course already exists', code=400):
        super().__init__(message, code)


class CourseAlreadyJoinedException(BaseServiceException):
    def __init__(self, message='The user have already joined this course', code=400):
        super().__init__(message, code)


class CourseSelectionNotFoundException(BaseServiceException):
    def __init__(self, message='Course selection not found', code=404):
        super().__init__(message, code)


class CourseRecordNotFoundException(BaseServiceException):
    def __init__(self, message='Course record not found', code=404):
        super().__init__(message, code)
