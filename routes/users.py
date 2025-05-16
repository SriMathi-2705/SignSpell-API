# routes/users.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from MODULE.USER.service.user_service import User

user_bp = Blueprint('user_bp', __name__, url_prefix='/users')

@user_bp.route('', methods=['GET'])
@jwt_required()
def list_users():
    return jsonify(User.list_users_service()), 200

@user_bp.route('', methods=['POST'])
@jwt_required()
def create_user():
    data = request.get_json() or {}
    data['User_ID'] = get_jwt_identity()
    return jsonify(User.save_user_service(data)), 201

@user_bp.route('/<int:lng_User_ID>', methods=['GET'])
@jwt_required()
def get_user(lng_User_ID):
    return jsonify(User.get_user_details(lng_User_ID)), 200

@user_bp.route('/<int:lng_User_ID>', methods=['PUT'])
@jwt_required()
def update_user(lng_User_ID):
    data = request.get_json() or {}
    data.update({'User_ID': get_jwt_identity(), 'lng_User_ID': lng_User_ID})
    return jsonify(User.update_user_service(data)), 200

@user_bp.route('/<int:lng_User_ID>', methods=['DELETE'])
@jwt_required()
def delete_user(lng_User_ID):
    return jsonify(User.delete_user_service(lng_User_ID)), 200
