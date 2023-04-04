# _*_ coding: utf-8 _*_
"""
Time:     2023/3/21 18:49
Author:   不做评论(vvbbnn00)
Version:  
File:     text.py
Describe: 
"""
import traceback

from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException

from exceptions import BaseServiceException

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/test'


@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return {
            "code": e.code,
            "message": e.description,
            "data": None
        }, e.code
    if isinstance(e, BaseServiceException):
        return {
            "code": e.code,
            "message": e.message,
            "data": None
        }, 400
    traceback.print_exc()
    return {
        "code": 500,
        "message": str(e),
        "data": None
    }, 500


if __name__ == '__main__':
    from api import api_blueprint

    app.register_blueprint(api_blueprint, url_prefix='/api/v1')
    app.run(debug=True, port=5001)
