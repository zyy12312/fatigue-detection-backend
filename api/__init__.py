# _*_ coding: utf-8 _*_
"""
Time:     2023/3/21 20:24
Author:   不做评论(vvbbnn00)
Version:  
File:     __init__.py.py
Describe: 
"""
from flask import Blueprint
from flask_restx import Api
from werkzeug.exceptions import HTTPException

api_blueprint = Blueprint('api', __name__, url_prefix='/api/v1')
api = Api(
    api_blueprint,
    version='1.0',
    title='Fatigue Detection Backend',
    authorizations={
        "AccessToken": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Generate access token in the settings page of your user account.",
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

from .v1.schema import (
    APIBaseResponseSchema,
    APIHttpErrorResponseSchema
)

api.schema_model("APIBaseResponseSchema", APIBaseResponseSchema)
api.schema_model("APIHttpErrorResponseSchema", APIHttpErrorResponseSchema)


from .v1.status import status_namespace
from .v1.users import user_namespace

api.add_namespace(status_namespace, '/status')
api.add_namespace(user_namespace, '/users')
