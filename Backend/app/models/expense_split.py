from app.extensions import db
from datetime import datetime

class ExpenseSplit(db.Model):
  __tablename__ = "expense_splits"

  id = db.Column(db.Integer, primary_key = True)
  expense_id = db.Column(db.Integer, db.ForeignKey("expenses.id"), nullable = False)
  user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable = False)
  amount_owed = db.Column(db.Numeric(10,2), nullable = False)

  # Relationships
  expense = db.relationship("Expense", back_populates = "splits")
  user = db.relationship("User")

  def __repr__(self):
    return f"<ExpenseSplit User {self.user_id} owes {self.amount_owed} for Expense {self.expense_id}>"