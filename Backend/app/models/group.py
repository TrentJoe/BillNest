from app.extensions import db
from datetime import datetime

class Group(db.Model):
  __tablename__ = "groups"

  id = db.Column(db.Integer, primary_key = True)
  name = db.Column(db.String(150), nullable = False)
  description = db.Column(db.String(255), nullable = True)
  created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable = False)
  created_at = db.Column(db.DateTime, default = datetime.utcnow)

  # Relationships
  memberships = db.relationship(
    "Membership",
    back_populates = "group",
    cascade = "all, delete-orphan"
  )

  creator = db.relationship("User")

  settlemetns = db.relationship(
    "Settlement",
    back_populates = "group",
    cascade = "all, delete-orphan"
  )
  
  def __repr__(self):
    return f"<Group {self.name}, created by {self.created_by}>"