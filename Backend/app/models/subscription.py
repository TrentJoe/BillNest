from app.extensions import db
from datetime import datetime

class Subscription(db.Model):
  __tablename__ = "subscriptions"

  id = db.Column(db.Integer, primary_key = True)
  name = db.Column(db.String(150), nullable = False)
  amount = db.Column(db.Numeric(10,2), nullable = False)

  billing_cycle = db.Column(
    db.String(20),
    nullable = False,
    default = "monthly" # e.g., monthly, yearly
  )
  next_billing_date = db.Column(db.Date,  nullable = False)

  owner_type = db.Column(
    db.String(20),
    nullable = False,
    default = "user"  # e.g., user, group
)

owner_id = db.Column(db.Integer, nullable = False)

created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable = False)

active = db.Column(db.Boolean, default = True)

#relationships

created_by_user = db.relationship("User")

def __repr__(self):
    return f"<Subscription {self.name}, Amount: {self.amount}, Cycle: {self.billing_cycle}>"
