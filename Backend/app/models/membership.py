from app.extensions import db
from datetime import datetime

class Membership(db.Model):
  __tablename__ = "memberships"

  id = db.Column(db.Integer, primary_key = True)
  user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable = False)
  group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable = False)
  role = db.Column(db.String, default = "member")  # e.g., member, admin
  joined_at = db.Column(db.DateTime, default = datetime.utcnow)

  # Relationships
  user = db.relationship("User", back_populates="memberships")
  group = db.relationship("Group", back_populates = "memberships")

  def __repr__(self):
    return f"<Memberships User {self.user_id} in Group {self.group_id} as {self.role}>"

  