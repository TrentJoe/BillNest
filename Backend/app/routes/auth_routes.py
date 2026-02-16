from flask import Blueprint, jsonify, request
from app.service.auth_service import AuthService

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    user = AuthService.register_user(email, password)

    return jsonify({"message": "User created successfully", "user_id": user.id}), 201


@auth_bp.route("/login", methods=[POST])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    token = AuthService.login_user(email, password)

    return token, 200


@auth_bp.route("/logout", methods=[POST])
def logout():
    AuthService.logout_user()
