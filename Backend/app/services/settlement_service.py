from app.models import Group, Expense, ExpenseSplit, Settlement
from app.extensions import db
from decimal import Decimal

def create_settlement_request(group, from_user, to_user, amount):
  """
  Create a settlement request between two users in a group.
  from_user_id claims they paid to_user_id £amount to settle their balance.
  The settlement starts with status "pending" and must be confirmed by to_user_id.

  Args:
      group (Group): The group in which the settlement is being made.
      from_user (User): The user who is claiming to have paid (the one settling their debt).
      to_user (User): The user who is being paid (the one owed money).
      amount (Decimal): The amount to be settled.
  
  Returns:
      Settlement: The created Settlement object.
  """
  # Validate that both users are members of the group
  from_user_membership = next(
    (m for m in group.memberships if m.user_id == from_user.id),
    None
  )

  to_user_membership = next(
    (m for m in group.memberships if m.user_id == to_user.id),
    None
  )

  if not from_user_membership or not to_user_membership:
    raise ValueError("Both users must be members of the group to create a settlement request.")

  # Validate that the amount is positive
  if amount <= Decimal("0.00"):
    raise ValueError("Settlement amount must be greater than zero.")
  
  # Validate that the from_user is not the same as to_user
  if from_user.id == to_user.id:
    raise ValueError("Cannot create a settlement request to yourself")

  # Create the settlement request
  new_settlement = Settlement(
    from_user_id = from_user.id,
    to_user_id = to_user.id,
    group_id = group.id,
    amount = amount,
    status = "pending"
  )
  db.session.add(new_settlement)
  db.session.commit()

  return new_settlement


def confirm_settlement(settlement, confirming_user):
  """
  Confirm a settlement request, marking it as completed.
  Only the user who is owed money (to_user) can confirm the settlement.

  Args:
      settlement (Settlement): The Settlement object to confirm.
      confirming_user (User): The ID of the user confirming the settlement (should be to_user)
  
  Returns:
      Settlement: The updated Settlement object with status "confirmed".
  """
  # Validate the settlement exists and is pending
  if not settlement:
    raise ValueError("Settlement request not found.")
  
  if settlement.status != "pending":
    raise ValueError("Only pending settlement requests can be confirmed.")
  
  # Validate that the confirming user is the to_user (the one owed money)
  if confirming_user.id != settlement.to_user_id:
    raise ValueError("Only the user who is owed money can confirm the settlement request.")
  
  # Update the settlement status to confirmed
  settlement.status = "confirmed"
  db.session.commit()

  return settlement

def reject_settlement(settlement, rejecting_user):
  """
  Reject a settlement request, marking it as rejected.
  Only the user who is owed money (to_user) can reject the settlement.

  Args:
      settlement (Settlement): The Settlement object to reject.
      rejecting_user (int): The ID of the user rejecting the settlement (should be to_user)
  
  Returns:
      Settlement: The updated Settlement object with status "rejected".
  """
  # Validate the settlement exists and is pending
  if not settlement:
    raise ValueError("Settlement request not found.") 

  if settlement.status != "pending":
    raise ValueError("Only pending settlement requests can be rejected.")
  
  # Validate that the rejecting user is the to_user (the one owed money)
  if rejecting_user != settlement.to_user_id:
    raise ValueError("Only the user who is owed money can reject the settlement request.")

  # Update the settlement status to rejected
  settlement.status = "rejected"
  db.session.commit()

  return settlement

def get_group_settlements(group):
  """
  Retrieve all settlements for a given group.

  Args:
      group (Group): The group for which to retrieve settlements.

  Returns:
      list of Settlement: A list of Settlement objects associated with the group.
  """
  return group.settlements

def get_user_unconfirmed_settlements(user):
  """
  Retrieve all pending/rejected settlements for a given user.

  Args:
      user (User): The user for which to retrieve pending settlements.
  
  Returns:
      list of Settlement: A list of pending/rejected Settlement objects
  """
  def get_user_unconfirmed_settlements(user):

    pending_received = [
        s for s in user.settlements_received
        if s.status == "pending"
    ]

    rejected_sent = [
        s for s in user.settlements_sent
        if s.status == "rejected"
    ]

    return {
        "pending_received": pending_received,
        "rejected_sent": rejected_sent
    }
