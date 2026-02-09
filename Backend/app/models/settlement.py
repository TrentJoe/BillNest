from app.extensions import db
from datetime import datetime

class Settlement(db.Model):
  __tablename__ = "settlements"

  id = db.Column(db.Integer, primary_key = True)

  from_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable = False)

  to_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable = False)

  group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable = False)

  amount = db.Column(db.Numeric(10,2), nullable = False)

  status = db.Column(db.String(20), nullable = False, default = "pending") # e.g., pending / confirmed / rejected

  created_at = db.Column(db.DateTime, default = datetime.utcnow)

  # Relationships
  from_user = db.relationship("User", foreign_keys = [from_user_id], back_populates = "settlements_sent")
  to_user = db.relationship("User", foreign_keys = [to_user_id], back_populates = "settlements_received")

  group = db.relationship("Group")



  def __repr__(self):
    return f"<Settlement from User {self.from_user_id} to User {self.to_user_id} in Group {self.group_id}, Status: {self.status}>"


