from extensions import (
    os,
    pymongo
)

client = pymongo.MongoClient(os.getenv('mongodb_endpoint'))


def user_exists(user_id):
    db = client['user']
    info = db['user_info']
    return info.find_one({'user_id': user_id})


def insert_user(data):
    if not user_exists(data['user_id']):
        db = client['user']
        info = db['user_info']
        data['createAt'] = datetime.now()
        data['access_type'] = ['user']
        info.update_one(
            {"user_id": data['user_id']},
            {"$set": data},
            upsert=True
        )

def fetch_user(user_id):
    db = client['user']
    info = db['user_info']
    return info.find_one(
        {
            'user_id': user_id,
            'active': True
        }
    )