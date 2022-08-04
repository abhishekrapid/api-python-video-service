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
    insert_user

)
from app.service.auth_middleware import token_required_redirect
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


@app.route("/google-login")
def google_login():
    # if current_user:
    #     return redirect(os.getenv('success_url'))
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("oauth2/v2/userinfo")
    if resp.ok:
        resp = resp.json()
        if fetch_user(resp['id']):
            return redirect(os.getenv('success_url'))
    return redirect(os.getenv('failed_url'))


@app.route('/google/callback')
def google_callback():
    response = {
        "success": False,
        "message": "Invalid parameters",
        "token": ""
    }
    resp = google.get("oauth2/v2/userinfo")
    if resp.ok:
        resp = resp.json()
        session['user_id'] = resp['id']
        user_info = {
            'user_id': resp['id'],
            'profile_url': resp['picture'],
            'user_name': resp['name'],
            'email': resp['email'],
            'active': True
        }
        insert_user(user_info)
        token = jwt.encode({
            'user_id': user_info['user_id'],
            'access_type': fetch_user(user_info['user_id'])['access_type'],
            'exp': datetime.utcnow() + timedelta(hours=1)
        }, app.config['SECRET_KEY'], "HS256")
        print(token)
        return redirect(f"os.getenv('success_url')/?token={token}")

    return redirect(os.getenv('failed_url'))