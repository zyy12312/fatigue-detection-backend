# _*_ coding: utf-8 _*_
"""
Time:     2023/4/11 18:39
Author:   不做评论(vvbbnn00)
Version:  
File:     courses.py
Describe: 
"""
from flask_restx import Namespace, Resource

from api.v1.helpers.auth import has_role
from api.v1.helpers.request import validate_args
from exceptions import BadRequestException, CourseNotFoundException, CourseAlreadyExistsException
from models import Course

course_namespace = Namespace(path='/courses', name="Courses", description='Operations related to courses')


@course_namespace.route('/course')
class CourseInfo(Resource):
    @course_namespace.doc(
        description='Get course info',
    )
    @has_role(['admin', 'teacher'])
    @validate_args({
        'id': (str, ...),
    },
        location='query',
    )
    def get(self, user, data):
        _id = data.get('id')
        course = Course.find_by_id(_id)
        if not course:
            raise CourseNotFoundException()

        if 'admin' not in user.roles:
            found = False
            teachers = Course.get_teachers(_id)
            for teacher in teachers:
                if teacher._id == user._id:
                    found = True
                    break
            if not found:
                raise CourseNotFoundException()

        return {
            'code': 200,
            'message': 'ok',
            'data': course.dict()
        }

    @course_namespace.doc(
        description='Create a course',
    )
    @has_role('admin')
    @validate_args({
        'course_name': (str, ...),
        'description': (str, ...),
    },
        location='json',
    )
    def post(self, user, data):
        course_name = data.get('course_name')
        description = data.get('description')
        course = Course(course_name=course_name, description=description)
        course.save()
        return {
            'code': 200,
            'message': 'ok',
            'data': course.dict()
        }

    @course_namespace.doc(
        description='Update a course',
    )
    @has_role('admin')
    @validate_args({
        'id': (str, ...),
        'course_name': (str, None),
        'description': (str, None),
    },
        location='json',
    )
    def put(self, user, data):
        _id = data.get('id')
        course_name = data.get('course_name')
        description = data.get('description')
        course = Course.find_by_id(_id)
        if not course:
            raise CourseNotFoundException()
        if course_name:
            course.course_name = course_name
        if description:
            course.description = description
        course.save()
        return {
            'code': 200,
            'message': 'ok',
            'data': course.dict()
        }

    @course_namespace.doc(
        description='Delete a course',
    )
    @has_role('admin')
    @validate_args({
        'id': (str, ...),
    },
        location='json',
    )
    def delete(self, user, data):
        _id = data.get('id')
        course = Course.find_by_id(_id)
        if not course:
            raise CourseNotFoundException()
        course.delete()
        return {
            'code': 200,
            'message': 'ok'
        }


@course_namespace.route('/list')
class CourseList(Resource):
    @course_namespace.doc(
        description='Get course list',
    )
    @has_role(['admin', 'teacher'])
    @validate_args({
        'page': (int, 1),
        'per_page': (int, 10),
        'course_id': (str, None),
        'course_name': (str, None),
    },
        location='query',
    )
    def get(self, user, data):
        page = data.get('page')
        if page < 1: page = 1
        per_page = data.get('per_page')
        if per_page < 1 or per_page > 100: per_page = 10
        query = {}
        if data.get('course_id'):
            query['course_id'] = data.get('course_id')
        if data.get('course_name'):
            query['course_name'] = {'$regex': data.get('course_name')}
        pipeline = []
        if 'admin' not in user.roles:  # 从CourseSelection查询是否有AS_TEACHER的记录
            pipeline.append({
                '$lookup': {
                    'from': 'courseselection',
                    'let': {'course_id_str': {'$toString': '$_id'}},
                    'pipeline': [
                        {
                            '$match': {
                                '$expr': {
                                    '$and': [
                                        {'$eq': ['$course_id', '$$course_id_str']},
                                        {'$eq': ['$user_id', str(user._id)]},
                                        {'$eq': ['$selection_type', 'AS_TEACHER']},
                                    ]
                                }
                            }
                        }
                    ],
                    'as': 'selections',
                }
            })
            pipeline.append({
                '$match': {
                    'selections': {'$ne': []},
                }
            })
            pipeline.append({
                '$project': {
                    'selections': 0,
                }})
        pipeline.append({
            '$match': query,
        })
        pipeline.append({
            '$skip': (page - 1) * per_page,
        })
        pipeline.append({
            '$limit': per_page,
        })
        courses = Course.aggregate(pipeline)

        return {
            'code': 200,
            'message': 'ok',
            'data': {
                'list': [course.dict() for course in courses],
                'total': len(courses),
                'has_next': len(courses) == per_page,
            }
        }
