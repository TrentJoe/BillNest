from app.extensions import db
from app.models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import uuid
from datetime import datetime, timedelta
from flask import current_app
from app.models.Blacklistedtoken import BlacklistedToken


def register_user(name, email, password):
  if not email and not password:
    raise ValueError("Email and password are required")
  
  existing_user = User.query.filter(User.email == email).first()

  if existing_user:
    raise ValueError("Email is already registered")
  
  password_hash = generate_password_hash(password)

  new_user = User(
    name = name,
    email = email,
    password_hash = password_hash
  )

  db.session.add(new_user)
  db.session.commit()

  return new_user


def login_user(email, password):

  if not email or not password:
    raise ValueError("Email and password are required")
  
  user = User.query.filter(User.email == email).first()

  if not user or not check_password_hash(user.password_hash, password):
    raise ValueError("Invalid email or password")
  
  token = jwt.encode(
    {
      "user_id": user.id,
      "jti": str(uuid.uuid4()),
      "exp": datetime.utcnow() + timedelta(hours=2)
    },
    current_app.config["SECRET_KEY"],
    algorithm="HS256"
  )

  return token


def logout_user(jti):
  # Blacklist the token by adding its jti to the BlacklistedToken table
  blacklist_token(jti)


def blacklist_token(jti):
  blacklisted = BlacklistedToken(jti=jti)
  db.session.add(blacklisted)
  db.session.commit()