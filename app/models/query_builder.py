from extensions import (
    os,
    pymongo,
    datetime
)
from bson.objectid import ObjectId
import re


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
    if 'admin' in user_data['roles'] or 'staff' in user_data['roles']:
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
                "cover_image": 1,
                "createAt": 1,
                "updateAt": 1
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
                "cover_image": 1,
                "createAt": 1,
                "updateAt": 1
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
                "createAt": 1,
                "updateAt": 1
            }
        )
    )


def fetch_users():
    db = client['user']
    info = db['user_info']
    return list(
        info.find(
            {},
            {
                '_id': 0
            }
        )
    )


def update_user(user_id, user_data):
    db = client['user']
    info = db['user_info']
    info.update_one(
        {
            'id': user_id
        },
        {
            "$set": user_data
        }
    )


def set_course(course_data):
    db = client['courses']
    info = db['course']
    course_data['createAt'] = datetime.now()
    course_data['updateAt'] = datetime.now()
    info.insert_one(course_data)


def update_course(course_id, course_data):
    db = client['courses']
    info = db['course']
    course_data['updateAt'] = datetime.now()
    info.update_one(
        {
            '_id': ObjectId(course_id)
        },
        {
            "$set": course_data
        }
    )


def delete_course(course_id):
    db = client['courses']
    info = db['course']
    info.delete_one({'_id': ObjectId(course_id)})
    db2 = client['courses']
    info2 = db['course_detail']
    info2.delete_many(
        {
            'course_id': course_id
        }
    )


def update_video_db(video_id, video_data):
    db = client['courses']
    info = db['course_detail']
    video_data['updateAt'] = datetime.now()
    info.update_one(
        {
            '_id': ObjectId(video_id)
        },
        {
            "$set": video_data
        }
    )


def delete_video_db(video_id):
    db = client['courses']
    info = db['course_detail']
    info.delete_one(
        {'_id': ObjectId(video_id)}
    )


def fetch_video_by_id(video_id, roles):
    db = client['courses']
    info = db['course_detail']
    if 'admin' in roles:
        query = {
            '_id': ObjectId(video_id)
        }
    else:
        query = {
            'course_id': ObjectId(video_id),
            'active': True
        }
    return info.find_one(
        query
    )


def insert_video(course_id, data):
    db = client['courses']
    info = db['course_detail']
    data['course_id'] = course_id
    data['createAt'] = datetime.now()
    data['updateAt'] = datetime.now()
    info.insert_one(data)


def search_courses_db(keyword, roles, limit):
    rgx = re.compile(f'.*{keyword}.*', re.IGNORECASE)
    db = client['courses']
    info = db['course']
    if 'admin' in roles:
        query = {
            'title': rgx
        }
    else:
        query = {
            'title': rgx,
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
                "cover_image": 1,
                "createAt": 1,
                "updateAt": 1
            }
        ).limit(limit)
    )


def filter_courses_db(filter, roles):
    db = client['courses']
    info = db['course']
    if 'admin' in roles:
        query = {
            "category": {"$in": filter.split(',')}
        }
    else:
        query = {
            "category": {"$in": filter.split(',')},
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
                "cover_image": 1,
                "createAt": 1,
                "updateAt": 1
            }
        )
    )