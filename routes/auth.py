# routes/auth.py

from flask import Blueprint, request, jsonify, url_for
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

from config import Config
from MODULE.USER.service.user_service import User
from MODULE.USER.util.user_util import encrypt_password
from CREATE_DB_CODE.tables_creation import tbl_User, connection

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')

serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
JWT_BLOCKLIST = set()

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json() or {}
    for f in ('str_First_Name','str_Last_Name','str_Email','str_Location','str_Password'):
        if not data.get(f):
            return jsonify({'ErrorCode':'9997','Message':'All fields required'}), 400

    data['User_ID'] = 0
    result = User.save_user_service(data)
    return jsonify(result), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email, pwd = data.get('str_Email'), data.get('str_Password')
    if not email or not pwd:
        return jsonify({'ErrorCode':'9997','Message':'Email & Password required'}), 400

    row = connection.execute(
        tbl_User.select().where(
            tbl_User.c.str_Email==email,
            tbl_User.c.bln_IsDeleted==False
        )
    ).fetchone()

    if not row or encrypt_password(pwd) != row.str_Password_hash:
        return jsonify({'ErrorCode':'9996','Message':'Invalid credentials'}), 401

    uid = str(row.lng_User_ID)
    
    return jsonify({
        'ErrorCode':'9999',
        'access_token': create_access_token(identity=uid, fresh=True),
        'refresh_token': create_refresh_token(identity=uid)
    }), 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    new_token = create_access_token(identity=get_jwt_identity(), fresh=False)
    return jsonify({'ErrorCode':'9999','access_token':new_token}), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    JWT_BLOCKLIST.add(get_jwt()['jti'])
    return jsonify({'ErrorCode':'9999','Message':'Logged out'}), 200

@auth_bp.route('/forgot', methods=['POST'])
def forgot_password():
    data = request.get_json() or {}
    email = data.get('str_Email')
    if not email:
        return jsonify({'ErrorCode':'9997','Message':'Email required'}), 400

    row = connection.execute(
        tbl_User.select().where(tbl_User.c.str_Email==email)
    ).fetchone()
    if not row:
        return jsonify({'ErrorCode':'9996','Message':'Email not found'}), 404

    token = serializer.dumps(email, salt='pw-reset')
    link  = url_for('auth_bp.reset_password', token=token, _external=True)
    # TODO: send `link` via email
    return jsonify({'ErrorCode':'9999','reset_url':link}), 200

@auth_bp.route('/reset/<token>', methods=['POST'])
def reset_password(token):
    try:
        email = serializer.loads(token, salt='pw-reset', max_age=3600)
    except SignatureExpired:
        return jsonify({'ErrorCode':'9995','Message':'Token expired'}), 400
    except BadSignature:
        return jsonify({'ErrorCode':'9996','Message':'Invalid token'}), 400

    data = request.get_json() or {}
    pwd  = data.get('str_Password')
    if not pwd:
        return jsonify({'ErrorCode':'9997','Message':'Password required'}), 400

    return jsonify(User.reset_password_service(email, encrypt_password(pwd))), 200
