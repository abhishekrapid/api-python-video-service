from extensions import (
    request,
    os,
    abort,
    redirect,
    jwt,
    wraps
)
from app.models.query_builder import (
    fetch_user
)


def token_required_redirect(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return redirect(os.getenv('failed_url'))
        try:
            data = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
            current_user = fetch_user(data["user_id"])
            if current_user is None:
                return redirect(os.getenv('failed_url'))
            if not current_user["active"]:
                abort(403)
        except Exception as e:
            print(e)
            return redirect(os.getenv('failed_url'))

        return f(current_user, *args, **kwargs)

    return decorated