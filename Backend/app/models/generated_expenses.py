from app.extensions import db
from datetime import datetime

class GeneratedExpense(db.Model):
  __tablename__ = "generated_expenses"

  id = db.Column(db.Integer, primary_key = True)

  subscription_id = db.Column(db.Integer, db.ForeignKey("subscriptions.id"), nullable = False)

  expense_id = db.Column(db.Integer, db.ForeignKey("expenses.id"), nullable = False, unique = True)

  billing_period = db.Column(db.String(7), nullable = False) # Format: 'MM-YYYY'

  created_at = db.Column(db.DateTime, default = datetime.utcnow)

  # Relationships
  subscription = db.relationship("Subscription", backref = "generated_expenses")

  expense = db.relationship("Expense")

  def __repr__(self):
    return f"<GeneratedExpense Subscription {self.subscription_id} for Expense {self.expense_id} in Period {self.billing_period}>"

