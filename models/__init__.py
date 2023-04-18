# _*_ coding: utf-8 _*_
"""
Time:     2023/3/20 20:08
Author:   不做评论(vvbbnn00)
Version:  
File:     __init__.py.py
Describe: 
"""
import time
from datetime import datetime
from enum import Enum

import jwt
import pydantic
from bson import ObjectId
from flask_pymongo import PyMongo

from exceptions import TokenInvalidError
from server import app
from config import JWT_SECRET_KEY, JWT_HASH_ALGORITHM, JWT_EXPIRATION_DELTA


class UserRole(Enum):
    STUDENT = 'Student'
    TEACHER = 'Teacher'
    ADMIN = 'Admin'


# class CourseSelectionType(Enum):
#     SELF_SELECT = 'SelfSelect'  # 自选
#     TEACHER_SELECT = 'TeacherSelect'  # 教师选课
#     ADMIN_SELECT = 'AdminSelect'  # 管理员选课
#     AS_TEACHER = 'AsTeacher'  # 作为教师选课
class BaseModel(object):
    @classmethod
    def _get_collection(cls):
        mongo = PyMongo(app)
        return mongo.db[cls.__name__.lower()]

    def __init__(self, **kwargs):
        self._id = None
        self.created_at = None
        self.updated_at = None
        for k, v in kwargs.items():
            setattr(self, k, v)

    def save(self):
        self.updated_at = datetime.now()
        mongo = PyMongo(app)
        if self._id is None:
            insert = self.__dict__
            insert.pop("_id")
            self.created_at = self.updated_at
            mongo.db[self.__class__.__name__.lower()].insert_one(insert)
        else:
            mongo.db[self.__class__.__name__.lower()].update_one({"_id": self._id}, {"$set": self.__dict__})

    def delete(self):
        mongo = PyMongo(app)
        if self._id is not None:
            mongo.db[self.__class__.__name__.lower()].delete_one({"_id": self._id})
            self._id = None

    @classmethod
    def find_by_id(cls, _id):
        mongo = PyMongo(app)
        data = mongo.db[cls.__name__.lower()].find_one({"_id": ObjectId(_id)})
        if data is None:
            return None
        return cls(**data)

    @classmethod
    def find_all(cls, limit=0, skip=0):
        mongo = PyMongo(app)
        if limit == 0:
            data_list = list(mongo.db[cls.__name__.lower()].find().skip(skip))
        else:
            data_list = list(mongo.db[cls.__name__.lower()].find().limit(limit).skip(skip))
        return [cls(**data) for data in data_list]

    @classmethod
    def query(cls, query, limit=0, skip=0):
        mongo = PyMongo(app)
        if limit == 0:
            data_list = list(mongo.db[cls.__name__.lower()].find(query).skip(skip))
        else:
            data_list = list(mongo.db[cls.__name__.lower()].find(query).limit(limit).skip(skip))
        return [cls(**data) for data in data_list]

    @classmethod
    def aggregate(cls, pipeline):
        mongo = PyMongo(app)
        data_list = list(mongo.db[cls.__name__.lower()].aggregate(pipeline))
        print(data_list)
        return [cls(**data) for data in data_list]

    def dict(self):
        data = self.__dict__
        for k, v in data.items():
            if isinstance(v, ObjectId):
                data[k] = str(v)
            if isinstance(v, datetime):
                data[k] = int(time.mktime(v.timetuple()))
            if isinstance(v, Enum):
                data[k] = v.value
        return data


class User(BaseModel):
    """
    User model
    """

    def __init__(self, _id=None, username=None, password=None, salt=None, phone=None, email=None, employee_id=None,
                 name=None, college=None, roles=None, **kwargs):
        super().__init__(_id=_id, **kwargs)
        self._get_collection()  # create index
        self.username = username
        self.password = password
        self.salt = salt
        self.phone = phone
        self.email = email
        self.employee_id = employee_id
        self.name = name
        self.college = college
        self.roles = roles if roles is not None else []

    @classmethod
    def _get_collection(cls):
        user_collection = super()._get_collection()
        user_collection.create_index("username", name="username_index", unique=True)
        user_collection.create_index("email", name="email_index", unique=True)
        user_collection.create_index("roles", name="roles_index", background=True)
        user_collection.create_index("username", name="username_index_desc", unique=True,
                                     collation={'locale': 'en', 'strength': 2})
        return user_collection

    @classmethod
    def find_by_username(cls, username):
        user_collection = User._get_collection()
        user_data = user_collection.find_one({"username": username})
        if user_data is None:
            return None
        return User(**user_data)

    def add_role(self, role: UserRole):
        role = role.value
        if role not in self.roles:
            self.roles.append(role)
            self.save()

    def remove_role(self, role: UserRole):
        role = role.value
        if role in self.roles:
            self.roles.remove(role)
            self.save()

    def has_role(self, role):
        role = role.value
        return role in self.roles

    def __str__(self):
        return f"User(id={self._id}, username={self.username}, name={self.name}, roles={self.roles})"


class CourseSelection(BaseModel):

    def __init__(self, _id=None, course_id=None, user_id=None, selection_type=None, **kwargs):
        super().__init__(_id=_id, **kwargs)
        self._get_collection()
        self.course_id = course_id
        self.user_id = user_id
        self.selection_type = selection_type

    def dict(self):
        data = super().dict()
        data["course"] = self.course.dict()
        data["user"] = self.user.dict()
        return data

    @property
    def course(self):
        course = Course.find_by_id(self.course_id)
        if course is None:
            return None
        return course

    @property
    def user(self):
        user = User.find_by_id(self.user_id)
        if user is None:
            return None
        del user.password
        del user.salt
        return user

    @classmethod
    def _get_collection(cls):
        course_selection_collection = super()._get_collection()
        course_selection_collection.create_index([("course_id", 1), ("user_id", 1)], name="course_id_user_id_index",
                                                 unique=True)
        course_selection_collection.create_index("course_id", name="course_id_index", background=True)
        course_selection_collection.create_index("user_id", name="user_id_index", background=True)
        course_selection_collection.create_index("selection_type", name="selection_type_index", background=True)
        return course_selection_collection

    @classmethod
    def find_by_course_id(cls, course_id, limit=0, skip=0):
        course_selection_collection = cls._get_collection()
        course_id = str(course_id)
        if limit > 0:
            course_selection_data = course_selection_collection.find({"course_id": course_id}).limit(limit).skip(skip)
        else:
            course_selection_data = course_selection_collection.find({"course_id": course_id}).skip(skip)
        return [CourseSelection(**data) for data in course_selection_data]

    @classmethod
    def find_by_user_id(cls, user_id, limit=0, skip=0):
        course_selection_collection = cls._get_collection()
        user_id = str(user_id)
        if limit > 0:
            course_selection_data = course_selection_collection.find({"user_id": user_id}).limit(limit).skip(skip)
        else:
            course_selection_data = course_selection_collection.find({"user_id": user_id}).skip(skip)
        return [CourseSelection(**data) for data in course_selection_data]


class Course(BaseModel):

    def __init__(self, _id=None, course_name=None, description=None,
                 **kwargs):
        super().__init__(_id=_id, **kwargs)
        self._get_collection()
        self.course_name = course_name
        self.description = description

    @classmethod
    def _get_collection(cls):
        course_collection = super()._get_collection()
        course_collection.create_index("course_name", name="course_name_index", unique=True)
        return course_collection

    @classmethod
    def get_teachers(cls, course_id):
        course_selections = CourseSelection.find_by_course_id(course_id)
        result = []
        for course_selection in course_selections:
            if course_selection.selection_type == 'AS_TEACHER':
                result.append(course_selection.user)
        return result

    @classmethod
    def get_students(cls, course_id):
        course_selections = CourseSelection.find_by_course_id(course_id)
        result = []
        for course_selection in course_selections:
            if course_selection.selection_type != "AS_TEACHER":
                result.append(course_selection.user)
        return result


class SubRecord(BaseModel):  # 学生听课记录
    record_id: str
    student_id: str
    start_time: int
    end_time: int
    detail: dict

    def __init__(self, _id=None, record_id=None, student_id=None, start_time=None, end_time=None, detail=None,
                 **kwargs):
        super().__init__(_id=_id, **kwargs)
        self._get_collection()
        self.record_id = record_id
        self.student_id = student_id
        self.start_time = start_time
        self.end_time = end_time
        self.detail = detail

    def dict(self):
        data = super().dict()
        data["student"] = self.student.dict() if self.student is not None else None
        data["record"] = self.record.dict() if self.record is not None else None
        return data

    @property
    def student(self):
        student = User.find_by_id(self.student_id)
        if student is None:
            return None
        del student.password
        del student.salt
        return student

    @property
    def record(self):
        record = Record.find_by_id(self.record_id)
        if record is None:
            return None
        return record

    @classmethod
    def _get_collection(cls):
        sub_record_collection = super()._get_collection()
        sub_record_collection.create_index("record_id", name="record_id_index", background=True)
        sub_record_collection.create_index("student_id", name="student_id_index", background=True)
        return sub_record_collection

    @classmethod
    def find_by_record_id(cls, record_id, limit=0, skip=0):
        sub_record_collection = cls._get_collection()
        if limit > 0:
            sub_record_data = sub_record_collection.find({"record_id": record_id}).limit(limit).skip(skip)
        else:
            sub_record_data = sub_record_collection.find({"record_id": record_id}).skip(skip)
        return [SubRecord(**data) for data in sub_record_data]

    @classmethod
    def find_by_student_id(cls, student_id, limit=0, skip=0):
        sub_record_collection = cls._get_collection()
        if limit > 0:
            sub_record_data = sub_record_collection.find({"student_id": student_id}).limit(limit).skip(skip)
        else:
            sub_record_data = sub_record_collection.find({"student_id": student_id}).skip(skip)
        return [SubRecord(**data) for data in sub_record_data]


class Record(BaseModel):  # 上课记录，
    course_id: str
    teacher_id: str
    start_time: int
    end_time: int
    status: int  # 0:未开始，1：进行中，2：已结束

    def __init__(self, _id=None, course_id=None, teacher_id=None, start_time=None, end_time=None, status=None,
                 **kwargs):
        super().__init__(_id=_id, **kwargs)
        self._get_collection()
        self.course_id = course_id
        self.teacher_id = teacher_id
        self.start_time = start_time
        self.end_time = end_time
        self.status = status

    def dict(self):
        data = super().dict()
        data["course"] = self.course.dict()
        data["teacher"] = self.teacher.dict()
        return data

    @property
    def course(self):
        course = Course.find_by_id(self.course_id)
        if course is None:
            return None
        return course

    @property
    def teacher(self):
        teacher = User.find_by_id(self.teacher_id)
        if teacher is None:
            return None
        del teacher.password
        del teacher.salt
        return teacher

    @classmethod
    def _get_collection(cls):
        record_collection = super()._get_collection()
        record_collection.create_index("course_id", name="course_id_index", background=True)
        record_collection.create_index("teacher_id", name="teacher_id_index", background=True)
        return record_collection

    @classmethod
    def find_by_course_id(cls, course_id, limit=0, skip=0):
        record_collection = cls._get_collection()
        if limit > 0:
            record_data = record_collection.find({"course_id": course_id}).limit(limit).skip(skip)
        else:
            record_data = record_collection.find({"course_id": course_id}).skip(skip)
        return [Record(**data) for data in record_data]


class Token:
    user: User
    iat: int
    exp: int
    iss: str

    def __init__(self, user=None, iat=None, exp=None, iss=None, **kwargs):
        if isinstance(user, dict):
            self.user = User(**user)
        else:
            self.user = user
        self.iat = int(iat)
        self.exp = int(exp)
        self.iss = iss
        if self.exp < time.time():
            raise TokenInvalidError("Token expired")
        if self.iat > time.time():
            raise TokenInvalidError("Token not valid yet")

    def pack(self):
        return jwt.encode({
            "user": {
                "_id": str(self.user._id),
                "username": self.user.username,
                "roles": self.user.roles
            },
            "iat": self.iat,
            "exp": self.exp,
            "iss": self.iss
        }, JWT_SECRET_KEY, algorithm=JWT_HASH_ALGORITHM)

    @staticmethod
    def unpack(token):
        try:
            data = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_HASH_ALGORITHM])
        except jwt.exceptions.InvalidTokenError:
            raise TokenInvalidError("Token invalid")
        return Token(**data)
