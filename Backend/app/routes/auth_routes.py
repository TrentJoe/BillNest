from flask import Blueprint, jsonify, request
from app.services import auth_service
from app.utils.auth_decorator import token_required
import jwt
from flask import current_app
from app.services.auth_service import blacklist_token

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
  try:
    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
      raise ValueError("Name, email and password are required")

    user = auth_service.register_user(
      name = data.get("name"),
      email = data.get("email"),
      password = data.get("password")
    )
  except ValueError as e:
    return jsonify({"message": str(e)}), 400

  return jsonify({"message": "User created successfully", "user_id": user.id}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
  try:
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    token = auth_service.login_user(
      email = data.get("email"),
      password = data.get("password")
    )
  except ValueError as e:
    return jsonify({"message": str(e)}), 400

  return jsonify({"token": token}), 200


@auth_bp.route("/logout", methods=["POST"])
@token_required
def logout(current_user):

  auth_header = request.headers.get("Authorization")
  token = auth_header.split(" ")[1]

  decoded = jwt.decode(
    token,
    current_app.config["SECRET_KEY"],
    algorithms=["HS256"],
    options={"verify_exp": False}  # Don't fail if token is expired, we just want the jti
  )

  blacklist_token(decoded["jti"])

  return jsonify({"message": "Logged out successfully"}), 200


@auth_bp.route("/me", methods=["GET"])
@token_required
def get_me(current_user):
  return jsonify({
    "id": current_user.id,
    "name": current_user.name,
    "email": current_user.email,
    "created_at": current_user.created_at.isoformat()
  }), 200

