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
from flask_cors import CORS, cross_origin
from dotenv import load_dotenv


load_dotenv()


app = Flask(__name__)
cors = CORS(app)
