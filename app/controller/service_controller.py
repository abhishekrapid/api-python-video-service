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
    timedelta,
    cross_origin
)
from app.models.query_builder import (
    fetch_user,
    insert_user,
    fetch_courses,
    fetch_course,
    fetch_videos,
    fetch_users,
    update_user,
    set_course,
    update_course,
    delete_course,
    update_video_db,
    delete_video_db,
    fetch_video_by_id,
    insert_video,
    search_courses_db,
    filter_courses_db
)
from app.service.auth_middleware import token_required_redirect, token_required_json
from flask_dance.contrib.google import make_google_blueprint, google
from app.service.video_provider import VideoProvider

api = Blueprint('user', 'user')


google_login = make_google_blueprint(
    client_id=os.getenv('client_id'),
    client_secret=os.getenv('client_secret'),
    redirect_url="/google/callback",
    scope=["profile", "email"]
)
app.register_blueprint(google_login, url_prefix='/googlelogin')


@api.route('/')
@cross_origin()
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
            'name': resp['name'],
            'email': resp['email'],
            'active': True
        }
        insert_user(user_info)
        token = jwt.encode({
            'id': user_info['id'],
            'roles': fetch_user(user_info['id'])['roles'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, app.config['SECRET_KEY'], "HS256")
        print(token)
        session['current_user_token'] = token
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
            'name': resp['name'],
            'email': resp['email'],
            'active': True
        }
        insert_user(user_info)
        token = jwt.encode({
            'id': user_info['id'],
            'roles': fetch_user(user_info['id'])['roles'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, app.config['SECRET_KEY'], "HS256")
        session['current_user_token'] = token
        return redirect(f"{os.getenv('success_url')}?token={token}")

    return redirect(os.getenv('failed_url'))


@api.route('/courses', methods=["GET"])
@cross_origin()
@token_required_json
def get_courses(current_user):
    response_json = {
        "status": 404,
        "message": "Something went wrong.",
        "items": []
    }
    response_json['items'] = fetch_courses(current_user)
    response_json['status'] = 200
    response_json['message'] = 'ok'
    return jsonify(response_json)


@app.route("/courses/<course_id>", methods=["GET"])
@cross_origin()
@token_required_json
def get_course(current_user, course_id):
    response_json = {
        "status": 404,
        "message": "Something went wrong.",
        "items": []
    }
    response_json['items'] = fetch_course(course_id, current_user['roles'])
    response_json['status'] = 200
    response_json['message'] = 'ok'
    return jsonify(response_json)


@app.route("/courses/<course_id>/videos", methods=["GET"])
@cross_origin()
@token_required_json
def get_videos(current_user, course_id):
    response_json = {
        "status": 404,
        "message": "Something went wrong.",
        "items": []
    }
    response_json['items'] = fetch_videos(course_id, current_user['roles'])
    response_json['status'] = 200
    response_json['message'] = 'ok'
    return jsonify(response_json)


@app.route("/admin")
@token_required_redirect
def get_admin_page(current_user):
    if 'admin' in current_user['roles']:
        return render_template('admin_dashboard.html', user_info=current_user)
    return redirect('/')


@app.route('/<manage_type>')
@token_required_json
def get_manage(current_user, manage_type):
    response_json = {
        "status": 404,
        "message": "Something went wrong.",
        "items": []
    }
    if 'admin' in current_user['roles']:
        if 'users' in manage_type:
            response_json['items'] = fetch_users()
            response_json['status'] = 200
            response_json['message'] = 'ok'
        elif 'courses' in manage_type:
            response_json['items'] = fetch_courses(current_user)
            response_json['status'] = 200
            response_json['message'] = 'ok'
    return jsonify(response_json)


@app.route('/<manage_type>/<object_id>', methods=['PUT'])
@token_required_json
def update_manage_detail(current_user, manage_type, object_id):
    response_json = {
        "status": 404,
        "message": "Something went wrong.",
        "items": []
    }
    if 'admin' in current_user['roles']:
        if 'users' in manage_type:
            if not request.form['active'] or not request.form['roles']:
                response_json['message'] = 'Field is missing.'
            else:
                user_data = request.form.to_dict()
                user_data['active'] = True if user_data['active'].lower() == 'true' else False
                user_data['roles'] = user_data['roles'].split(',')
                update_user(object_id, user_data)
                response_json['items'] = fetch_users()
                response_json['status'] = 200
                response_json['message'] = 'ok'
        elif 'courses' in manage_type:
            if not request.form['category'] or not request.form['title'] or not request.form['active'] or not request.form['description']:
                response_json['message'] = 'Field is missing.'
            else:
                course_data = request.form.to_dict()
                course_data['active'] = True if course_data['active'].lower() == 'true' else False
                update_course(object_id, course_data)
                response_json['items'] = fetch_courses(current_user)
                response_json['status'] = 200
                response_json['message'] = 'ok'
    return jsonify(response_json)


@app.route('/courses', methods=['POST'])
@token_required_json
def post_manage(current_user):
    response_json = {
        "status": 404,
        "message": "Something went wrong.",
        "items": []
    }
    if 'admin' in current_user['roles']:
        if not request.form['category'] or not request.form['title'] or not request.form['active'] or not request.form['description']:
            response_json['message'] = 'Field is missing.'
        else:
            course_data = request.form.to_dict()
            course_data['active'] = True if course_data['active'].lower() == 'true' else False
            set_course(course_data)
            response_json['items'] = fetch_courses(current_user)
            response_json['status'] = 200
            response_json['message'] = 'ok'
    return jsonify(response_json)


@app.route('/courses/<object_id>', methods=['DELETE'])
@token_required_json
def delete_manage_detail(current_user, object_id):
    response_json = {
        "status": 404,
        "message": "Something went wrong.",
        "items": []
    }
    if 'admin' in current_user['roles']:
        video_info = fetch_videos(object_id, current_user['roles'])
        if video_info:

            file_name_list = [{"Key": i['video_path']} for i in video_info]
            vp = VideoProvider()
            vp.delete_videos(file_name_list)
            # [{"Key": "text/test7.txt"}, {"Key": "text/test8.txt"}]
        delete_course(object_id)
        response_json['status'] = 200
        response_json['message'] = 'ok'
    return jsonify(response_json)


@app.route('/videos/<video_id>', methods=['PUT'])
@token_required_json
def update_video(current_user, video_id):
    response_json = {
        "status": 404,
        "message": "Something went wrong.",
        "items": []
    }
    if 'admin' in current_user['roles']:
        if not request.form['title'] or not request.form['description'] or not request.form['active']:
            response_json['message'] = 'Field is missing.'
        else:
            video_data = {
                'active': request.form['active'],
                'description': request.form['description'],
                'title': request.form['title']
            }

            video_data['active'] = True if video_data['active'].lower() == 'true' else False
            update_video_db(video_id, video_data)
            response_json['items'] = fetch_videos(request.form['course_id'], current_user['roles'])
            response_json['status'] = 200
            response_json['message'] = 'ok'

    return jsonify(response_json)


@app.route('/videos/<video_id>', methods=['DELETE'])
@token_required_json
def delete_video(current_user, video_id):
    response_json = {
        "status": 404,
        "message": "Something went wrong.",
    }
    if 'admin' in current_user['roles']:
        video_info = fetch_video_by_id(video_id, current_user['roles'])
        if video_info:
            vp = VideoProvider()
            vp.delete_video(video_info['video_path'])
            delete_video_db(video_id)
            response_json['status'] = 200
            response_json['message'] = 'ok'

    return jsonify(response_json)


@app.route('/videos')
@token_required_redirect
def get_video(current_user):
    if 'admin' in current_user['roles'] or 'staff' in current_user['roles']:
        return render_template('upload_video.html', user_info=current_user, course_list=[{"id": i['_id'], "title": i['title']} for i in fetch_courses(current_user)])
    else:
        return redirect('/')


def video_exists_server(video_info):
    status = False
    if video_info.get('server_storage'):
        status = True
    return status


@app.route('/videos/<video_id>')
@token_required_json
def get_video_url(current_user, video_id):
    response_json = {
        "status": 404,
        "message": "Something went wrong.",
        }
    video_info = fetch_video_by_id(video_id, current_user['roles'])
    if video_info:
        status = video_exists_server(video_info)
        if status:
            response_json['server_storage'] = True
            response_json['video_url'] = video_info['server_path']
        else:
            vp = VideoProvider()
            response_json['server_storage'] = False
            response_json['video_url'] = vp.generate_url(video_info['video_path'])
        response_json['status'] = 200
        response_json['message'] = 'ok'

    return jsonify(response_json)


@app.route('/download/<video_id>')
@token_required_json
def download_video(current_user, video_id):
    response_json = {
        "status": 404,
        "message": "Something went wrong.",
    }
    video_info = fetch_video_by_id(video_id, current_user['roles'])
    vp = VideoProvider()
    if not os.path.exists('static'):
        os.mkdir('static')
    if not os.path.exists('static/video_file'):
        os.mkdir('static/video_file')
    server_path = f'static/video_file/{video_info["video_path"]}'
    status = vp.download_video_from_provider(video_info['video_path'], server_path)
    if status:
        video_data = {
            'server_storage': True,
            'server_path': server_path
        }
        update_video_db(video_id, video_data)
        response_json['status'] = 200
        response_json['message'] = 'ok'


@app.route('/generate-presigned-url', methods=['POST'])
@token_required_json
def generate_presigned_url(current_user):
    response_json = {
        "status": 404,
        "message": "Something went wrong.",
    }
    if 'admin' in current_user['roles'] or 'staff' in current_user['roles']:
        vp = VideoProvider()
        response_json['presigned_object'] = vp.generate_pre_signed_url(
            f'{fetch_course(request.form["course"], current_user["roles"])[0]["title"].replace("/", "").lower()}/{request.form["title"].replace("/", "")}.{request.form["file_name"].split(".")[-1]}')
        response_json['message'] = 'ok'
        response_json['status'] = 200
    else:
        response_json['message'] = 'Unauthorized'
        response_json['status'] = 401
    return jsonify(response_json)


@app.route('/videos', methods=['POST'])
@token_required_json
def post_video(current_user):
    response_json = {
        "status": 404,
        "message": "Something went wrong.",
    }
    if 'admin' in current_user['roles'] or 'staff' in current_user['roles']:
        if not request.form['course'] or not request.form['title'] or not request.form['description'] or not request.form['file_name']:
            response_json = {
                'status': 404,
                'message': 'Field is missing.'
            }
        else:
            # vp = VideoProvider()
            # response_json['presigned_object'] = vp.generate_pre_signed_url(
            #     f'{fetch_course(request.form["course"], current_user["roles"])[0]["title"].replace("/", "").lower()}/{request.form["title"].replace("/", "")}.{request.form["file_name"].split(".")[-1]}')
            video_info = {
                'title': request.form['title'],
                'description': request.form['description'],
                'video_path': f'{fetch_course(request.form["course"], current_user["roles"])[0]["title"].replace("/", "").lower()}/{request.form["title"].replace("/", "")}.{request.form["file_name"].split(".")[-1]}',
                'active': True
            }
            insert_video(request.form['course'], video_info)
            response_json['status'] = 200
            response_json['message'] = 'ok'
    else:
        response_json['message'] = 'Unauthorized'
        response_json['status'] = 401
    return jsonify(response_json)


@app.route('/search')
@cross_origin()
@token_required_json
def search_courses(current_user):
    response_json = {
        "status": 404,
        "message": "Something went wrong.",
    }
    response_json['items'] = search_courses_db(request.args['query'], current_user['roles'], request.args.get('limit', 20))
    response_json['status'] = 200
    response_json['message'] = 'ok'
    return jsonify(response_json)


@app.route('/filter')
@cross_origin()
@token_required_json
def filter_courses(current_user):
    response_json = {
        "status": 404,
        "message": "Something went wrong.",
    }
    response_json['items'] = filter_courses_db(request.args['query'], current_user['roles'])
    response_json['status'] = 200
    response_json['message'] = 'ok'
    return jsonify(response_json)


@app.errorhandler(403)
def forbidden(e):
    return redirect('/')


@app.errorhandler(404)
def forbidden(e):
    return redirect('/')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
