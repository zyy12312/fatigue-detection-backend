# _*_ coding: utf-8 _*_
"""
Time:     2023/3/28 20:08
Author:   不做评论(vvbbnn00)
Version:  
File:     __init__.py.py
Describe: 
"""
import json

from pydantic import BaseModel


class APIBaseResponseSchema(BaseModel):

    @classmethod
    def __str__(cls):
        ret = {}
        for k, v in cls.__dict__.items():
            if not k.startswith('__'):
                ret[k] = v
        return json.dumps(ret, ensure_ascii=False)


class APIHttpErrorResponseSchema(APIBaseResponseSchema):
    code: int = 200
    message: str = 'Internal Server Error'
    error: list = []
