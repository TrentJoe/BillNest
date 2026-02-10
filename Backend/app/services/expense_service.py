from app.models import *
from decimal import Decimal 
from app.extensions import db

def create_expense(group, creator_user, description, total_amount, splits, date):
  """
  Create a new expense with its splits.

  Args:
      group (Group): The group to which the expense belongs.
      creator_user (User): The user who created the expense.
      description (str): A description of the expense.
      total_amount (Decimal): The total amount of the expense.
      splits (list of dict): A list of splits, where each split is a dict with 'user_id' and 'amount_owed'.
      date (datetime): The date of the expense.

  Returns:
      Expense: The created Expense object.
  """

  # Validate input data
  if description is None or description.strip() == "":
    raise ValueError("Description cannot be empty.")

  if total_amount <= Decimal("0.00"):
    raise ValueError("Total amount must be greater than zero.")
  
  # Validate creator belongs to the group
  creator = next(
    (m for m in group.memberships if m.user_id == creator_user.id),
    None
  )
  if not creator:
    raise ValueError("Creator user must be a member of the group.")

  # Ensure all split users belong to the group
  validate_split_users(group, splits)
  # Ensure no duplicate split users
  validate_no_duplicate_split_users(group, splits)
  # Ensure split amounts sum to total_amount
  validate_split_amounts(total_amount, splits)
  # Create the expense
  new_expense = Expense(
    group_id = group.id,
    created_by = creator_user.id,
    description = description,
    total_amount = total_amount,
    date = date
  )
  # Create ExpenseSplit entries for each split
  for split in splits:
    new_expense.splits.append(
      ExpenseSplit(
        user_id=split["user"],
        amount_owed=split["amount"]
    )
)

  # Commit to database and return the created expense
  db.session.add(new_expense)
  db.session.commit()

  return new_expense


def delete_expense(group, expense, requesting_user):
  """
  Delete an expense if the requesting user is the admin.

  Args:
      expense (Expense): The expense to be deleted.
      requesting_user (User): The user requesting the deletion.

  Returns:
      bool: True if deletion was successful, False otherwise.
  """

  # Check requesting user is a member of the group
  requestor = next(
    (m for m in group.memberships if m.user_id == requesting_user.id),
    None 
  )
  if not requestor:
    raise ValueError("Requesting user must be a member of the group.")

  # check requesting user is an admin
  if requestor.role != "admin":
    raise ValueError("Only admins can delete expenses.")

  # Check if the expense exists
  expense_to_remove = next(
    (e for e in group.expenses if e.id == expense.id),
    None
  )
  if not expense_to_remove:
    raise ValueError("Expense does not exist in the group.")

  # If checks pass, delete the expense and its splits (cascade should handle this)
  db.session.delete(expense_to_remove)
  # Commit to database and return True if successful
  db.session.commit()
  return True

def get_group_expenses(group):
  """
  Retrieve all expenses for a given group.

  Args:
      group (Group): The group for which to retrieve expenses.
  Returns:
      list of Expense: A list of Expense objects belonging to the group.
  """
  # Return the list of expenses for the group (group.expenses should work due to relationship)
  return group.expenses

def get_expense_details(expense):
  """
  Retrieve details of a specific expense, including its splits.

  Args:
      expense (Expense): The expense for which to retrieve details.
  Returns:
      Expense: The Expense object with its splits loaded.
  """
  if not expense:
    raise ValueError("Expense not found.")

  return expense  # Due to relationships, expense.splits will be available when accessed

# Validation helpers (can be used inside the above functions)

def validate_split_users(group, splits):
  """
  Validate that all users in the splits belong to the group.

  Args:
      group (Group): The group to check against.
      splits (list of dict): The list of splits to validate.
  Raises:
      ValueError: If any split user does not belong to the group.
  """
  for split in splits:
    user = next(
      (m for m in group.memberships if m.user_id == split["user"]),
      None
    )
    if not user:
      raise ValueError(f"User with ID {split['user']} in splits does not belong to the group.")
  
  return True

def validate_no_duplicate_split_users(splits):
  """
  Validate that there are no duplicate users in the splits.

  Args:
      splits (list of dict): The list of splits to validate.
  Raises:
      ValueError: If there are duplicate users in the splits.
  """
  seen = set()

  for split in splits:
    user_id = split["user"]
    
    if user_id in seen:
      raise ValueError(f"Duplicate user with ID {user_id} found in splits.")
      
    seen.add(user_id)
  
  return True
  

def validate_split_amounts(total_amount, splits):
  """
  Validate that the sum of split amounts equals the total amount.

  Args:
      total_amount (Decimal): The total amount of the expense.
      splits (list of dict): The list of splits to validate.
  Raises:
      ValueError: If the sum of split amounts does not equal the total amount.
  """
    split_total = sum(
      Decimal(split["amount"]) for split in splits 
      )

    if split_total != total_amount:
      raise ValueError(f"The sum of split amounts ({split_total}) does not equal the total amount ({total_amount}).")

  return True


  