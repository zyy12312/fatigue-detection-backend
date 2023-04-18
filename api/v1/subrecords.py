# _*_ coding: utf-8 _*_
"""
Time:     2023/4/18 19:51
Author:   不做评论(vvbbnn00)
Version:  
File:     subrecords.py
Describe: 
"""
from flask_restx import Namespace, Resource

from api.v1.helpers.auth import has_role
from api.v1.helpers.request import validate_args
from exceptions import BadRequestException, CourseNotFoundException, CourseRecordNotFoundException, \
    UserNotFoundException
from models import Record, Course, User, CourseSelection, SubRecord

subrecords_namespace = Namespace(path='/subrecords', name="SubRecords", description='Operations related to subrecords')


def getSubRecord(record_id, user_id):
    record = Record.find_by_id(record_id)
    if not record:
        raise CourseRecordNotFoundException()

    course_list = CourseSelection.find_by_user_id(user_id)
    check = False
    course_id_list = [x.course_id for x in course_list]
    if record.course_id in course_id_list:
        check = True
    if not check:
        raise CourseRecordNotFoundException()

    user_id = str(user_id)
    record_id = str(record_id)
    subrecord_list = SubRecord.query({'record_id': record_id, 'user_id': user_id}, limit=1)
    if len(subrecord_list) == 0:
        sub_record = SubRecord(record_id=record_id, user_id=user_id)
        sub_record.detail = {}
        sub_record.student_id = user_id
        sub_record.save()
        return sub_record
    return subrecord_list[0]


@subrecords_namespace.route('/subrecord')
class SubRecordInfo(Resource):

    @subrecords_namespace.doc(
        description='Get subrecord info',
    )
    @has_role(['admin', 'teacher'])
    @validate_args({
        'id': (str, ...),
    },
        location='query',
    )
    def get(self, user, data):
        _id = data.get('id')
        subrecord = SubRecord.find_by_id(_id)
        if not subrecord:
            raise CourseRecordNotFoundException()
        record = subrecord.record
        check = False
        if 'admin' in user.roles:
            check = True
        elif 'teacher' in user.roles:
            if record.teacher_id == user._id:
                check = True
        if not check:
            raise CourseRecordNotFoundException()
        return {
            'code': 200,
            'message': 'ok',
            'data': subrecord.dict()
        }


@subrecords_namespace.route('/report')
class SubRecordReport(Resource):
    @subrecords_namespace.doc(
        description='Post subrecord report',
    )
    @has_role(['student'])
    @validate_args({
        'record_id': (str, ...),
        'start_time': (int, ...),
        'end_time': (int, ...),
        'status': (int, ...),  # 0: normal, 1: tired, 2: error
    },
        location='json',
    )
    def post(self, user, data):
        record_id = data.get('record_id')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        status = data.get('status')
        if start_time > end_time:
            raise BadRequestException('start_time > end_time')
        if status not in [0, 1, 2]:
            raise BadRequestException('status not in [0, 1, 2]')
        subrecord = getSubRecord(record_id, user._id)
        detail = subrecord.detail
        record_list = detail.get('record_list', [])
        record_list.append({
            'start_time': start_time,
            'end_time': end_time,
            'status': status
        })
        detail['record_list'] = record_list
        subrecord.detail = detail
        subrecord.save()
        return {
            'code': 200,
            'message': 'ok',
        }
