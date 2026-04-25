from app.extensions import db
from app.models.user import User
import jwt
from datetime import datetime, timedelta
from flask import current_app
from app.models.Blacklistedtoken import BlacklistedToken


def register_user(username, email, password):
  if not email or not password:
    return {"error": "Email and password are required"}
  
  existing_user = User.query.filter(User.email == email).first()
  if existing_user:
    return {"error": "Email already registered"}
  
  # Check if username already exists
  existing_username = User.query.filter(User.name == username).first()
  if existing_username:
    return {"error": "Username already taken"}

  # Create and save the new user
  user = User(name=username, email=email)
  user.set_password(password)

  db.session.add(user)
  db.session.commit()

  return {"user_id": user.id}


def login_user(email, password):

  user = User.query.filter(User.email == email).first()

  # Check user exists and password is correct
  if not user or not user.check_password(password):
    return {"error": "Invalid email or password"}

  # Generate JWT token
  token = jwt.encode(
    {
      "user_id": user.id,
      "exp": datetime.utcnow() + timedelta(hours=24)
    },
    current_app.config["SECRET_KEY"],
    algorithm="HS256"
  )

  return {"token": token}


def logout_user(token):
  try:
    # Decode to get the jti (JWT ID) from the token
    decoded = jwt.decode(
      token,
      current_app.config["SECRET_KEY"],
      algorithms=["HS256"]
    )

    # Check if already blacklisted
    existing = BlacklistedToken.query.filter(
      BlacklistedToken.jti == str(decoded["user_id"])
    ).first()

    if existing:
      return {"error": "Token already blacklisted"}

    # Add to blacklist
    blacklisted = BlacklistedToken(jti=str(decoded["user_id"]))
    db.session.add(blacklisted)
    db.session.commit()

    return {"message": "Successfully logged out"}

  except jwt.ExpiredSignatureError:
    return {"error": "Token has expired"}
  except jwt.InvalidTokenError:
    return {"error": "Invalid token"}


def blacklist_token(jti):
  """
  Directly blacklists a token by its JTI.
  Used internally by the auth decorator.
  """
  blacklisted = BlacklistedToken(jti=jti)
  db.session.add(blacklisted)
  db.session.commit()