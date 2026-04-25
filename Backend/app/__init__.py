from flask import Flask
from .config import Config
from .extensions import db, migrate, jwt
from app.routes.auth_routes import auth_bp
from app.routes.group_routes import group_bp
from app.routes.expense_routes import expense_bp
from app.exceptions import AppError
from flask import jsonify


def create_app():
  app = Flask(__name__)
  app.config.from_object(Config)

  db.init_app(app)
  migrate.init_app(app, db)
  jwt.init_app(app)

  from app import models
  from app.models.Blacklistedtoken import BlacklistedToken

  @app.errorhandler(AppError)
  def handle_app_error(e):
    # e is the exception that was raised
    # e.message is what you set in the exception
    # e.status_code is the HTTP code
    return jsonify({"message" : e.message}), e.status_code

  app.register_blueprint(auth_bp, url_prefix="/api/auth")
  app.register_blueprint(group_bp, url_prefix="/api")
  app.register_blueprint(expense_bp, url_prefix="/api")

  return app
