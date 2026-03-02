from functools import wraps
from flask import request, jsonify, current_app
import jwt
from app.models.user import User
from app.models.Blacklistedtoken import BlacklistedToken

def token_required(f):
  @wraps(f)
  def decorated(*args, **kwargs):

    auth_header = request.headers.get("Authorization")

    if not auth_header:
      return jsonify({"error": "Token is missing!"}), 401

    try:
      token = auth_header.split(" ")[1]

      decoded = jwt.decode(
        token,
        current_app.config["SECRET_KEY"],
        algorithms=["HS256"]
    )

      # Check blacklist
      blacklisted = BlacklistedToken.query.filter_by(
          jti=decoded["jti"]
      ).first()

      if blacklisted:
          return jsonify({"error": "Token has been revoked"}), 401

      current_user = User.query.get(decoded["user_id"])

      if not current_user:
          return jsonify({"error": "User not found"}), 401

    except jwt.ExpiredSignatureError:
      return jsonify({"error": "Token has expired!"}), 401
    
    except jwt.InvalidTokenError:
      return jsonify({"error": "Invalid token!"}), 401
    
    return f(current_user, *args, **kwargs)

  return decorated