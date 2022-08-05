from extensions import (
    request,
    os,
    abort,
    redirect,
    jwt,
    wraps,
    jsonify,
    app
)
from app.models.query_builder import (
    fetch_user
)


def token_required_redirect(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'X-Access-Token' in request.headers:
            token = request.headers['X-Access-Token']
        if not token:
            return redirect(os.getenv('failed_url'))
        try:
            data = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
            current_user = fetch_user(data["id"])
            if current_user is None:
                return redirect(os.getenv('failed_url'))
            if not current_user["active"]:
                abort(403)
        except Exception as e:
         #   print(e)
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
            token = request.headers['X-Access-Token']
        # return 401 if token is not passed
        if not token:
            return jsonify({'message': 'Token is missing !!'}), 401

        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = fetch_user(data["id"])
            if current_user is None:
                return jsonify({
                    'message': 'Unauthorized'
                }), 401
            if not current_user["active"]:
                abort(403)

        except:
            return jsonify({
                'message': 'Token is invalid !!'
            }), 401
        # returns the current logged in users contex to the routes
        return f(current_user, *args, **kwargs)

    return decorated
