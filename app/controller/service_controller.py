from extensions import (
    Blueprint,
    session,
    redirect,
    request,
    render_template,
    app,
    url_for,
    os,
    jsonify,
    jwt,
    datetime,
    timedelta
)
from app.models.query_builder import (
    fetch_user,
    insert_user,
    fetch_courses

)
from app.service.auth_middleware import token_required_redirect, token_required_json
from flask_dance.contrib.google import make_google_blueprint, google


api = Blueprint('user', 'user')


google_login = make_google_blueprint(
    client_id=os.getenv('client_id'),
    client_secret=os.getenv('client_secret'),
    redirect_url="/google/callback",
    scope=["profile", "email"]
)
app.register_blueprint(google_login, url_prefix='/googlelogin')


@api.route('/')
@token_required_redirect
def home(current_user):
    if current_user:
        return redirect(os.getenv('success_url'))
    return redirect(os.getenv('failed_url'))


@api.route("/google-login")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    try:
        resp = google.get("oauth2/v2/userinfo")
    except:
        return redirect(url_for("google.login"))
    if resp.ok:
        resp = resp.json()
        session['user_id'] = resp['id']
        user_info = {
            'id': resp['id'],
            'profile_url': resp['picture'],
            'user_name': resp['name'],
            'email': resp['email'],
            'active': True
        }
        insert_user(user_info)
        token = jwt.encode({
            'id': user_info['id'],
            'roles': fetch_user(user_info['id'])['access_type'],
            'exp': datetime.utcnow() + timedelta(hours=1)
        }, app.config['SECRET_KEY'], "HS256")
        print(token)
        return redirect(f"{os.getenv('success_url')}/?token={token}")
    return redirect(os.getenv('failed_url'))


@api.route('/google/callback')
def google_callback():
    resp = google.get("oauth2/v2/userinfo")
    if resp.ok:
        resp = resp.json()
        session['id'] = resp['id']
        user_info = {
            'id': resp['id'],
            'profile_url': resp['picture'],
            'user_name': resp['name'],
            'email': resp['email'],
            'active': True
        }
        insert_user(user_info)
        token = jwt.encode({
            'id': user_info['id'],
            'roles': fetch_user(user_info['id'])['access_type'],
            'exp': datetime.utcnow() + timedelta(hours=1)
        }, app.config['SECRET_KEY'], "HS256")
        print(token)
        return redirect(f"{os.getenv('success_url')}/?token={token}")

    return redirect(os.getenv('failed_url'))


@api.route('/courses')
@token_required_json
def courses(current_user):
    response_json = {
        "status": 404,
        "message": "Something went wrong.",
        "items": []
    }
    print(current_user)
    response_json['items'] = fetch_courses(current_user)
    response_json['status'] = 200
    response_json['message'] = 'ok'
    return jsonify(response_json)