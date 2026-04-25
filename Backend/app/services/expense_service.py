from app.models import *
from decimal import Decimal
from app.extensions import db
from app.models.group import Group
from app.models.expense import Expense
from app.models.expense_split import ExpenseSplit


def create_expense(group_id, creator_user, description, total_amount, splits=None, split_equally=False, date=None):
  group = Group.query.get(group_id)
  if not group:
    return {"error": "Group not found"}

  if not description or description.strip() == "":
    return {"error": "Description cannot be empty"}

  try:
    total_amount = Decimal(str(total_amount))
  except Exception:
    return {"error": "Invalid total amount"}

  if total_amount <= Decimal("0.00"):
    return {"error": "Total amount must be greater than zero"}

  creator = next((m for m in group.memberships if m.user_id == creator_user.id), None)
  if not creator:
    return {"error": "Creator user must be a member of the group"}

  if split_equally:
    members = [m.user_id for m in group.memberships]
    split_amount = (total_amount / Decimal(len(members))).quantize(Decimal("0.01"))
    splits = [{"user": uid, "amount": split_amount} for uid in members]

  if not splits:
    return {"error": "Splits are required"}

  split_validation = _validate_splits(group, splits, total_amount)
  if "error" in split_validation:
    return split_validation

  new_expense = Expense(
    group_id=group.id,
    created_by=creator_user.id,
    description=description,
    total_amount=total_amount,
    date=date,
  )
  for split in splits:
    new_expense.splits.append(
      ExpenseSplit(user_id=split["user"], amount_owed=split["amount"])
    )
  db.session.add(new_expense)
  db.session.commit()
  return {"expense_id": new_expense.id}


def delete_expense(group_id, expense_id):
  group = Group.query.get(group_id)
  if not group:
    return {"error": "Group not found"}
  expense = Expense.query.get(expense_id)
  if not expense or expense.group_id != group_id:
    return {"error": "Expense not found in group"}
  db.session.delete(expense)
  db.session.commit()
  return {"message": "Expense deleted successfully"}


def get_group_expenses(group_id):
  group = Group.query.get(group_id)
  if not group:
    return {"error": "Group not found"}
  expenses = []
  for e in group.expenses:
    expenses.append({
      "expense_id": e.id,
      "description": e.description,
      "total_amount": str(e.total_amount),
      "date": str(e.date) if e.date else None,
      "created_by": e.created_by,
    })
  return {"expenses": expenses}


def get_expense_details(expense_id):
  expense = Expense.query.get(expense_id)
  if not expense:
    return {"error": "Expense not found"}
  splits = []
  for s in expense.splits:
    splits.append({"user_id": s.user_id, "amount_owed": str(s.amount_owed)})
  return {
    "expense_id": expense.id,
    "description": expense.description,
    "total_amount": str(expense.total_amount),
    "date": str(expense.date) if expense.date else None,
    "created_by": expense.created_by,
    "splits": splits,
  }


def update_expense(group_id, expense_id, current_user, data):
  group = Group.query.get(group_id)
  if not group:
    return {"error": "Group not found"}
  expense = Expense.query.get(expense_id)
  if not expense or expense.group_id != group_id:
    return {"error": "Expense not found in group"}

  description = data.get("description")
  total_amount = data.get("total_amount")
  splits = data.get("splits")

  if description is not None:
    if description.strip() == "":
      return {"error": "Description cannot be empty"}
    expense.description = description

  if total_amount is not None:
    try:
      total_amount = Decimal(str(total_amount))
    except Exception:
      return {"error": "Invalid total amount"}
    if total_amount <= Decimal("0.00"):
      return {"error": "Total amount must be greater than zero"}
    expense.total_amount = total_amount

  if splits is not None:
    split_validation = _validate_splits(group, splits, expense.total_amount)
    if "error" in split_validation:
      return split_validation
    expense.splits.clear()
    for split in splits:
      expense.splits.append(
        ExpenseSplit(user_id=split["user"], amount_owed=split["amount"])
      )

  db.session.commit()
  return {
    "expense_id": expense.id,
    "description": expense.description,
    "total_amount": str(expense.total_amount),
  }


def _validate_splits(group, splits, total_amount):
  member_ids = {m.user_id for m in group.memberships}
  seen = set()
  for split in splits:
    uid = split["user"]
    if uid not in member_ids:
      return {"error": f"User {uid} is not a member of the group"}
    if uid in seen:
      return {"error": f"Duplicate user {uid} in splits"}
    seen.add(uid)
  split_total = sum(Decimal(str(s["amount"])) for s in splits)
  if split_total != Decimal(str(total_amount)):
    return {"error": f"Split amounts ({split_total}) do not equal total amount ({total_amount})"}
  return {"ok": True}
