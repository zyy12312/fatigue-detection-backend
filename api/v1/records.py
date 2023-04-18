# _*_ coding: utf-8 _*_
"""
Time:     2023/4/18 18:11
Author:   不做评论(vvbbnn00)
Version:  
File:     record.py
Describe: 
"""

from flask_restx import Namespace, Resource

from api.v1.helpers.auth import has_role
from api.v1.helpers.request import validate_args
from exceptions import BadRequestException, CourseNotFoundException, CourseRecordNotFoundException, \
    UserNotFoundException
from models import Record, Course, User, CourseSelection

records_namespace = Namespace(path='/records', name="Records", description='Operations related to records')


@records_namespace.route('/record')
class RecordInfo(Resource):
    @records_namespace.doc(
        description='Get record info',
    )
    @has_role(['admin', 'teacher', 'student'])
    @validate_args({
        'id': (str, ...),
    },
        location='query',
    )
    def get(self, user, data):
        _id = data.get('id')
        record = Record.find_by_id(_id)
        if not record:
            raise CourseRecordNotFoundException()
        check = False
        if 'admin' in user.roles:
            check = True
        elif 'teacher' in user.roles:
            if record.teacher_id == user._id:
                check = True
        elif 'student' in user.roles:
            course_list = CourseSelection.find_by_user_id(user._id)
            print(course_list)
            course_id_list = [x.course_id for x in course_list]
            if record.course_id in course_id_list:
                check = True
        if not check:
            raise CourseRecordNotFoundException()
        return {
            'code': 200,
            'message': 'ok',
            'data': record.dict()
        }

    @records_namespace.doc(
        description='Create a record',
    )
    @has_role(['admin', 'teacher'])
    @validate_args({
        'course_id': (str, ...),
        'start_time': (int, ...),
        'end_time': (int, ...),
        'status': (int, ...),
        'teacher_id': (str, None),
    },
        location='json',
    )
    def post(self, user, data):
        course_id = data.get('course_id')
        teacher_id = data.get('teacher_id')
        status = data.get('status')
        if status not in [0, 1, 2]:
            raise BadRequestException("Status must be 0, 1 or 2")

        start_time = data.get('start_time')
        end_time = data.get('end_time')

        if start_time > end_time:
            raise BadRequestException("Start time must be less than end time")
        course = Course.find_by_id(course_id)
        if not course:
            raise CourseNotFoundException()
        if 'admin' not in user.roles:
            teacher_id = user._id
        else:
            if teacher_id is None:
                raise BadRequestException()

        teacher_list = Course.get_teachers(course_id)
        found = False
        for teacher in teacher_list:
            if teacher._id == teacher_id:
                found = True
                break
        if not found:
            raise CourseNotFoundException("Teacher not found in course")

        record = Record(course_id=course_id,
                        teacher_id=teacher_id,
                        status=status,
                        start_time=start_time,
                        end_time=end_time)
        record.save()
        return {
            'code': 200,
            'message': 'ok',
            'data': record.dict()
        }

    @records_namespace.doc(
        description='Update a record',
    )
    @has_role(['admin', 'teacher'])
    @validate_args({
        'id': (str, ...),
        'course_id': (str, None),
        'start_time': (int, None),
        'end_time': (int, None),
        'status': (int, None),
        'teacher_id': (str, None),
    },
        location='json',
    )
    def put(self, user, data):
        _id = data.get('id')

        record = Record.find_by_id(_id)
        if not record:
            raise CourseRecordNotFoundException()
        if 'admin' not in user.roles and user._id != record.teacher_id:
            raise CourseRecordNotFoundException()

        course_id = data.get('course_id')
        teacher_id = data.get('teacher_id')
        status = data.get('status')
        if status is not None and status not in [0, 1, 2]:
            raise BadRequestException("Status must be 0, 1 or 2")

        start_time = data.get('start_time')
        end_time = data.get('end_time')

        if course_id is not None and 'admin' in user.roles:
            record.course_id = course_id
        if teacher_id is not None and 'admin' in user.roles:
            record.teacher_id = teacher_id
        if status is not None:
            record.status = status
        if start_time is not None:
            record.start_time = start_time
        if end_time is not None:
            record.end_time = end_time

        if record.start_time > record.end_time:
            raise BadRequestException("Start time must be less than end time")

        record.save()
        return {
            'code': 200,
            'message': 'ok',
            'data': record.dict()
        }

    @records_namespace.doc(
        description='Delete a record',
    )
    @has_role('admin')
    @validate_args({
        'id': (str, ...),
    },
        location='json',
    )
    def delete(self, user, data):
        _id = data.get('id')
        record = Record.find_by_id(_id)
        if not record:
            raise CourseRecordNotFoundException()
        record.delete()
        return {
            'code': 200,
            'message': 'ok',
            'data': record.dict()
        }


@records_namespace.route('/list')
class RecordList(Resource):
    @records_namespace.doc(
        description='Get record list',
    )
    @has_role(['admin', 'teacher', 'student'])
    @validate_args({
        'page': (int, 1),
        'per_page': (int, 10),
        'course_id': (str, None),
        'teacher_id': (str, None),
        'status': (int, None)
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
        if data.get('teacher_id') and 'admin' in user.roles:
            query['teacher_id'] = data.get('teacher_id')
        elif 'teacher' in user.roles and 'admin' not in user.roles:
            query['teacher_id'] = user._id
        if data.get('record_type'):
            query['status'] = data.get('status')
        pipeline = []
        if 'student' in user.roles:  # CourseSelection中判断课程是否已选
            pipeline.append({
                '$lookup': {
                    'from': 'courseselection',
                    'let': {'course_id_str': {'$toString': '$course_id'}},
                    'pipeline': [
                        {
                            '$match': {
                                '$expr': {
                                    '$and': [
                                        {'$eq': ['$course_id', '$$course_id_str']},
                                        {'$eq': ['$user_id', str(user._id)]},
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
            query['status'] = {
                '$in': [0, 1]  # 0: 未开始, 1: 进行中
            }
        pipeline.append({
            '$match': query
        })

        pipeline.append({
            '$sort': {
                'start_time': -1
            }
        })
        pipeline.append({
            '$skip': (page - 1) * per_page
        })
        pipeline.append({
            '$limit': per_page
        })
        record_list = Record.aggregate(pipeline)
        return {
            'code': 200,
            'message': 'ok',
            'data': {
                'list': [record.dict() for record in record_list],
                'total': len(record_list),
                'has_next': len(record_list) == per_page
            }
        }
