from app.extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
  __tablename__ = "users"

  id = db.Column(db.Integer, primary_key = True)
  name = db.Column(db.String(150), nullable = False)
  email = db.Column(db.String(255), unique = True, nullable = False)
  password_hash = db.Column(db.String(255), nullable = False)
  created_at = db.Column(db.DateTime, default = datetime.utcnow)

  # Relationships
  memberships = db.relationship(
    "Membership",
    back_populates = "user",
    cascade = "all, delete-orphan"
  )

  settlements_sent = db.relationship(
    "Settlement",
    foreign_keys = "Settlement.from_user_id",
    back_populates = "from_user",
  )

  settlements_received = db.relationship(
    "Settlement",
    foreign_keys = "Settlement.to_user_id",
    back_populates = "to_user",
  )

  def set_password(self, password):
    self.password_hash = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password_hash, password)

  def __repr__(self):
    return f"<User {self.name}, {self.email}>"