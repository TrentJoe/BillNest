from app.extensions import db
from datetime import datetime

class BlacklistedToken(db.Model):
  __tablename__ = "blacklisted_tokens"

  id = db.Column(db.Integer, primary_key = True)
  jti = db.Column(db.String(36), nullable = False, unique = True)
  created_at = db.Column(db.DateTime, default = datetime.utcnow)