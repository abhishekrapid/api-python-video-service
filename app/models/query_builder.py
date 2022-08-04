from extensions import (
    os,
    pymongo
)

client = pymongo.MongoClient(os.getenv('mongodb_endpoint'))


def fetch_user(user_id):
    db = client['user']
    info = db['user_info']
    return info.find_one(
        {
            'user_id': user_id,
            'active': True
        }
    )