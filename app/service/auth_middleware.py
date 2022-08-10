from extensions import (
    request,
    os,
    abort,
    redirect,
    jwt,
    wraps,
    jsonify,
    app,
    session
)
from app.models.query_builder import (
    fetch_user
)


def token_required_redirect(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # if 'X-Access-Token' in request.headers:
        #     token = request.headers['X-Access-Token']
        if 'current_user_token' in session:
            token = session['current_user_token']
        if not token:
            session.clear()
            return redirect(os.getenv('failed_url'))
        try:
            data = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
            current_user = fetch_user(data["id"])
            if current_user is None:
                session.clear()
                return redirect(os.getenv('failed_url'))
            if not current_user["active"]:
                session.clear()
                abort(403)
        except Exception as e:
            #   print(e)
            session.clear()
            return redirect(os.getenv('failed_url'))

        return f(current_user, *args, **kwargs)

    return decorated


# decorator for verifying the JWT
def token_required_json(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if 'X-Access-Token' in request.headers:
            token = request.headers['Authentication']
        #    token = session['current_user_token']
        # return 401 if token is not passed
        if not token:
            session.clear()
            return jsonify({'message': 'Token is missing !!', 'status': 401}), 401

        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = fetch_user(data["id"])
            if current_user is None:
                session.clear()
                return jsonify({
                    'message': 'Unauthorized',
                    'status': 401
                }), 401
            if not current_user["active"]:
                session.clear()
                abort(403)

        except:
            session.clear()
            return jsonify({
                'message': 'Token is invalid !!',
                'status': 401
            }), 401
        # returns the current logged in users contex to the routes
        return f(current_user, *args, **kwargs)

    return decorated
