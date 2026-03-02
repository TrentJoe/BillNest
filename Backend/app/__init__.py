from flask import Flask
from .config import Config
from .extensions import db, migrate, jwt
from app.routes.auth_routes import auth_bp
from app.routes.group_routes import group_bp
# expense_bp, payment_bp, user_bp, membership_bp, notification_bp, settlement_bp


def create_app():
  app = Flask(__name__)
  app.config.from_object(Config)

  db.init_app(app)
  migrate.init_app(app, db)
  jwt.init_app(app)

  # Import models to register them with SQLAlchemy
  from app import models
  from app.models.Blacklistedtoken import BlacklistedToken

  # Register blueprints
  app.register_blueprint(auth_bp, url_prefix="/api/auth")
  app.register_blueprint(group_bp, url_prefix="/api")

  return app
