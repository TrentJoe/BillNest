from app.extensions import db
from datetime import datetime

class User(db.Model):
  __tablename__ = "users"

  id = db.Column(db.Integer, primary_key = True)
  name = db.Column(db.String(150), nullable = False)
  email = db.Column(db.String(255), unique = True, nullable = False)
  password_hash = db.Column(db.String(255), nullable = False)
  created_at = db.Column(db.DateTime, default = datetime.utcnow)

  # Relationships
  memberships = db.relationship(
    "Memberships",
    back_populates = "user",
    cascade = "all, delete-orphan"
  )

  settlements_sent = db.relationship(
    "Settlement",
    foreign_keys = "Settlement.from_user_id",
    backref = "from_user",
  )

  settlements_received = db.relationship(
    "Settlement",
    foreign_keys = "settlement.to_user_id",
    backref = "to_user",
  )

  def __repr__(self):
    return f"<User {self.name}, {self.email}>"