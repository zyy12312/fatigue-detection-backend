# _*_ coding: utf-8 _*_
"""
Time:     2023/3/28 20:01
Author:   不做评论(vvbbnn00)
Version:  
File:     __init__.py.py
Describe: 
"""
from flask import Blueprint
from flask_restx import Api

api_blueprint = Blueprint('api', __name__, url_prefix='/api/v1')
api = Api(
    api_blueprint,
    version='1.0',
    title='Fatigue Detection Backend',
    description='API documentation for Fatigue Detection Backend.',
    authorizations={
        "AccessToken": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Start with `Bearer `, followed by the access token. This is the only way to access the API.",
        },
        "ContentType": {
            "type": "apiKey",
            "in": "header",
            "name": "Content-Type",
            "description": "Must be set to `application/json`",
        },
    },
    security=["AccessToken", "ContentType"],
)

from .schema import (
    APIBaseResponseSchema,
    APIHttpErrorResponseSchema
)

api.schema_model("APIBaseResponseSchema", APIBaseResponseSchema)
api.schema_model("APIHttpErrorResponseSchema", APIHttpErrorResponseSchema)

from .status import status_namespace
from .users import user_namespace
from .courses import course_namespace
from .course_selection import course_selection_namespace
from .records import records_namespace
from .subrecords import subrecords_namespace

api.add_namespace(status_namespace, '/status')
api.add_namespace(user_namespace, '/users')
api.add_namespace(course_namespace, '/courses')
api.add_namespace(course_selection_namespace, '/course_selection')
api.add_namespace(records_namespace, '/records')
api.add_namespace(subrecords_namespace, '/subrecords')
