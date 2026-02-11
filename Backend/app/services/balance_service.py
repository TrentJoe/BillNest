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


  
def get_group_obligations(group):
  """
    Returns:
        {
            debtor_id: {
                creditor_id: Decimal(amount)
            }
        }
    """
  obligations = defaultdict(lambda: defaultdict(lambda:Decimal("0.00")))

# Process expenses and splits to determine who owes whom
for expense in group.expenses:
  payer_id = expense.created_by

  for split in expense.splits:
    debtor_id = split.user_id
    amount = split.amount_owed

    if debtor_id == payer_id:
      continue  # Skip if the debtor is the same as the payer

    obligations[debtor_id][payer_id] += amount
  
# Process confirmed settlements

for settlement in group.settlements:
  if settlement.status != "confirmed":
    continue

  debtor_id = settlement.from_user_id
  creditor_id = settlement.to_user_id
  amount = settlement.amount

  obligations[debtor_id][creditor_id] -= amount
  
  # Clean up zero or negative obligations
  if obligations[debtor_id][creditor_id] <= Decimal("0.00"):
    del obligations[debtor_id][creditor_id]
  
  
  if not obligations[debtor_id]:  # If debtor has no more obligations, remove them
    del obligations[debtor_id]

  return obligations

def get_user_obligations(group, user_id):

  all_obligations = get_group_obligations(group)
  owes = all_obligations.get(user_id, {})

  owed_by = {}

  for debtor, creditors in all_obligations.items():
    if user_id in creditors:
      owed_by[debtor] = creditors[user_id]
  
  return{
    "owes": owes,
    "owed_by": owed_by
  }

