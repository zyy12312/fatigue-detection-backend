# _*_ coding: utf-8 _*_
"""
Time:     2023/4/11 19:38
Author:   不做评论(vvbbnn00)
Version:  
File:     course_selection.py
Describe: 
"""

from flask import request
from flask_restx import Namespace, Resource, fields

from api.v1.helpers.auth import has_role
from api.v1.helpers.request import validate_args
from exceptions import BadRequestException, CourseNotFoundException, CourseAlreadyExistsException, \
    CourseAlreadyJoinedException, CourseSelectionNotFoundException
from models import Course, CourseSelection, User

course_selection_namespace = Namespace(path='/course_selection', name="CourseSelection",
                                       description='Operations related to course selection')


@course_selection_namespace.route('/selection')
class CourseSelectionInfo(Resource):
    @course_selection_namespace.doc(
        description='Get course selection info',
    )
    @has_role('admin')
    @validate_args({
        'id': (str, ...)
    },
        location='query',
    )
    def get(self, user, data):
        _id = data.get('id')
        course_selection = CourseSelection.find_by_id(_id)
        if not course_selection:
            raise CourseSelectionNotFoundException()
        return {
            'code': 200,
            'message': 'ok',
            'data': course_selection.dict()
        }

    @course_selection_namespace.doc(
        description='Create a course selection',
    )
    @has_role('admin')
    @validate_args({
        'course_id': (str, ...),
        'user_id': (str, ...),
        'selection_type': (str, ...),
    },
        location='json',
    )
    def post(self, user, data):
        course_id = data.get('course_id')
        user_id = data.get('user_id')
        selection_type = data.get('selection_type')

        course = Course.find_by_id(course_id)
        if not course:
            raise CourseNotFoundException()
        student = User.find_by_id(user_id)
        if not student:
            raise BadRequestException()
        course_selection = CourseSelection.query({
            'course_id': course_id,
            'user_id': user_id
        })
        if course_selection:
            raise CourseAlreadyJoinedException()

        course_selection = CourseSelection(course_id=course_id,
                                           user_id=user_id,
                                           selection_type=selection_type)
        course_selection.save()

        return {
            'code': 200,
            'message': 'ok',
            'data': course_selection.dict()
        }

    @course_selection_namespace.doc(
        description='Delete a course selection',
    )
    @has_role('admin')
    @validate_args({
        'id': (str, ...),
    },
        location='json',
    )
    def delete(self, user, data):
        _id = data.get('id')
        course_selection = CourseSelection.find_by_id(_id)
        if not course_selection:
            raise CourseSelectionNotFoundException()
        course_selection.delete()
        return {
            'code': 200,
            'message': 'ok'
        }


@course_selection_namespace.route('/list')
class CourseSelectionList(Resource):
    @course_selection_namespace.doc(
        description='Get course selection list',
    )
    @has_role('admin')
    @validate_args({
        'page': (int, 1),
        'per_page': (int, 10),
        'course_id': (str, None),
        'user_id': (str, None),
        'selection_type': (str, None),
    },
        location='query',
    )
    def get(self, user, data):
        page = data.get('page')
        if page < 1: page = 1
        per_page = data.get('per_page')
        if per_page < 1 or per_page > 100: per_page = 10
        course_id = data.get('course_id')
        user_id = data.get('user_id')
        selection_type = data.get('selection_type')

        query = {}
        if course_id:
            query['course_id'] = course_id
        if user_id:
            query['user_id'] = user_id
        if selection_type:
            query['selection_type'] = selection_type

        course_selections = CourseSelection.query(query, per_page, (page - 1) * per_page)
        return {
            'code': 200,
            'message': 'ok',
            'data': {
                'list': [course_selection.dict() for course_selection in course_selections],
                'total': len(course_selections),
                'has_next': len(course_selections) == per_page
            }
        }
