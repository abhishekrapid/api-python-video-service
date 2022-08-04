from flask import (
    Flask,
    Blueprint,
    session,
    redirect,
    request,
    render_template,
    url_for,
    jsonify,
    abort
)
import os
import jwt
from datetime import datetime, timedelta
import pymongo
from functools import wraps


app = Flask(__name__)