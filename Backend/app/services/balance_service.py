from collections import defaultdict
from decimal import Decimal

from app.models import Group, Expense, ExpenseSplit, Settlement

def calculate_group_balances(group):
  """
  Calculate net balances for each user in the group.
  
  Positive balance  -> user is owed money
  Negative balance  -> user owes money

  Balances are derived from:
    - expenses (who paid)
    - expense splits (who owed)
    - confirmed settlements only

  Args:
      group (Group): The group for which to calculate balances.

  Returns:
      dict: A dictionary mapping user IDs to their net balance as Decimal.
  """
  # Start everyone at 0 balance
  # defaultdict means if a user_id key doesn't exist, it auto-creates it with 0.00
  balances = defaultdict(lambda: Decimal("0.00"))

  # Process expenses in the group and their splits
  for expense in group.expenses:
    payer_id = expense.created_by
    # Person who PAID gets amount added to their balance
    balances[payer_id] += expense.total_amount

    for split in expense.splits:
      # Person who OWED gets amount subtracted from their balance
      balances[split.user_id] -= split.amount_owed

  # Process confirmed settlements in the group (when someone pays someone back)
  for settlement in group.settlements:
    # Only process confirmed settlements
    if settlement.status != "confirmed":
      continue

    # Person who paid back (from_user) reduces their debt
    balances[settlement.from_user_id] += settlement.amount
    # Person who received payment (to_user) is owed less
    balances[settlement.to_user_id] -= settlement.amount

  # Validate that balances sum to zero (ensures no money is created or lost)
  total = sum(balances.values())
  if total != Decimal("0.00"):
    raise ValueError(f"Balances do not sum to zero! Total: {total}")

  return balances


