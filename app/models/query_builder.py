from extensions import (
    os,
    pymongo,
    datetime
)
from bson.objectid import ObjectId


client = pymongo.MongoClient(os.getenv('mongodb_endpoint'))


def user_exists(user_id):
    db = client['user']
    info = db['user_info']
    return info.find_one({'id': user_id})


def insert_user(data):
    if not user_exists(data['id']):
        db = client['user']
        info = db['user_info']
        data['createAt'] = datetime.now()
        data['roles'] = ['user']
        info.update_one(
            {"id": data['id']},
            {"$set": data},
            upsert=True
        )


def fetch_user(user_id):
    db = client['user']
    info = db['user_info']
    return info.find_one(
        {
            'id': user_id,
            'active': True
        }
    )


def fetch_courses(user_data):
    db = client['courses']
    info = db['course']
    if 'admin' in user_data['roles']:
        query = {}
    else:
        query = {
            'active': True
        }
    return list(
        info.find(
            query,
            {
                "_id": {
                    "$toString": "$_id"
                },
                "title": 1,
                "category": 1,
                "active": 1,
                "description": 1,
                "url": 1
            }
        )
    )


def fetch_course(course_id, roles):
    db = client['courses']
    info = db['course']
    if 'admin' in roles:
        query = {
            '_id': ObjectId(course_id)
        }
    else:
        query = {
            '_id': ObjectId(course_id),
            'active': True
        }
    return list(
        info.find(
            query,
            {
                "_id": {
                    "$toString": "$_id"
                },
                "title": 1,
                "category": 1,
                "active": 1,
                "description": 1,
                "url": 1
            }
        )
    )


def fetch_videos(course_id, roles):
    db = client['courses']
    info = db['course_detail']
    if 'admin' in roles:
        query = {
            'course_id': course_id
        }
    else:
        query = {
            'course_id': course_id,
            'active': True
        }
    return list(
        info.find(
            query,
            {
                "_id": {
                    "$toString": "$_id"
                },
                "title": 1,
                "video_path": 1,
                "active": 1,
                "description": 1,
                "createdAt": 1
            }
        )
    )