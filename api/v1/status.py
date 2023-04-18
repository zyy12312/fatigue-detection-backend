# _*_ coding: utf-8 _*_
"""
Time:     2023/3/28 20:01
Author:   不做评论(vvbbnn00)
Version:  
File:     status.py
Describe: 
"""

from flask_restx import Namespace, Resource

from . import APIHttpErrorResponseSchema

status_namespace = Namespace(path='/status', name="Status", description='API Status')


@status_namespace.route('')
@status_namespace.doc(
    description='Get API Status',
)
class Status(Resource):
    def get(self):
        resp = APIHttpErrorResponseSchema()
        resp.message = 'ok'
        return resp.dict()
