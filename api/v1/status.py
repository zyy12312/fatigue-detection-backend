# _*_ coding: utf-8 _*_
"""
Time:     2023/3/28 20:01
Author:   不做评论(vvbbnn00)
Version:  
File:     status.py
Describe: 
"""

from flask_restx import Namespace, Resource

from api import APIHttpErrorResponseSchema

status_namespace = Namespace('status', description='Status')


@status_namespace.route('')
class Status(Resource):
    def get(self):
        resp = APIHttpErrorResponseSchema()
        resp.message = 'ok'
        return resp.dict()
