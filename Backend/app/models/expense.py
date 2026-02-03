from app.extensions import db
from datetime import datetime

class Expense(db.Model):
  __tablename__ = "expenses"

  id = db.Column(db.Integer, primary_key = True)
  group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable = False)
  created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable = False)
  description = db.Column(db.String(255), nullable = False)
  total_amount = db.Column(db.Numeric(10,2), nullable = False)
  date = db.Column(db.DateTime, nullable  = False)
  created_at = db.Column(db.DateTime, default = datetime.utcnow)

  # Relationships
  group = db.relationship("Group", backref = "expenses") # backref builds both doors of the relationship
  creator = db.relationship("User")

  splits = db.relationship("ExpenseSplit", back_populates = "expense", # back_populates builds one door of the relationship (expense.splits) -> the other door is built in ExpenseSplit model (splits.expense)
    cascade = "all, delete-orphan"
  )

  def __repr__(self):
    return f"<Expense {self.description} of {self.total_amount} in Group {self.group_id}>"
