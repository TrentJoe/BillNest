"""
POST /auth/register  - Register a new user
POST /auth/login     - Login and receive a JWT token
POST /auth/logout    - Logout and blacklist the token
"""
from flask import Blueprint, request, jsonify
from app.utils.auth_decorator import token_required
from app.services import auth_service

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
  
  data = request.get_json(silent=True)

  if not data:
    return jsonify({"message": "Invalid JSON data. Send a valid JSON body with Content-Type: application/json"}), 400

  username = data.get("username")
  email = data.get("email")
  password = data.get("password")

  if not username or not email or not password:
    return jsonify({"message": "Name, email and password are required"}), 400

  user = auth_service.register_user(
    username = data.get("username"),
    email = data.get("email"),
    password = data.get("password")
  )

  if "error" in user:
    return jsonify({"message": user["error"]}), 400

  return jsonify({"message": "User created successfully", "user_id": user["user_id"]}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
  
  data = request.get_json(silent=True)
  if not data:
    return jsonify({"message": "Invalid JSON data. Send a valid JSON body with Content-Type: application/json"}), 400

  email = data.get("email")
  password = data.get("password")

  if not email or not password:
    return jsonify({"message": "Email and password are required"}), 400

  result = auth_service.login_user(
    email = data.get("email"),
    password = data.get("password")
  )
  if "error" in result:
    return jsonify({"message": result["error"]}), 400

  return jsonify({
    "message": "Login successful",
    "token": result["token"]
  }), 200


@auth_bp.route("/logout", methods=["POST"])
@token_required
def logout(current_user):

  auth_header = request.headers.get("Authorization")
  token = auth_header.split(" ")[1]

  result = auth_service.logout_user(token=token)

  if "error" in result:
    return jsonify({"message": result["error"]}), 400

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

