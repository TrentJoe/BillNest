from app.extensions import db
from app.services import expense_service
from app.models import Subscription, GeneratedExpense, Group, User
from datetime import datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta


def create_subscription(
    name, amount, billing_cycle, next_billing_date, owner_type, owner_id, created_by
):

    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    if billing_cycle not in ["daily", "weekly", "monthly", "yearly"]:
        raise ValueError(
            "Invalid billing cycle. Must be one of: daily, weekly, monthly, yearly."
        )

    if next_billing_date <= datetime.now(timezone.utc):
        raise ValueError("Next billing date must be in the future.")

    if owner_type not in ["user", "group"]:
        raise ValueError("Invalid owner type. Must be 'user' or 'group'.")

    if not owner_id:
        raise ValueError("Owner ID must be provided.")

    if next_billing_date.tzinfo is None:
        next_billing_date = next_billing_date.replace(tzinfo=timezone.utc)

    if next_billing_date <= datetime.now(timezone.utc):
        raise ValueError("Next billing date must be in the future.")

    new_subscription = Subscription(
        name=name,
        amount=amount,
        billing_cycle=billing_cycle,
        next_billing_date=next_billing_date,
        owner_type=owner_type,
        owner_id=owner_id,
        created_by=created_by,
    )

    db.session.add(new_subscription)
    db.session.commit()

    return new_subscription


def update_subscription(subscription, name, amount, billing_cycle, next_billing_date):
    # Vallidation check for subscription object
    if subscription is None:
        raise ValueError("Subscription not found.")

    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    if billing_cycle not in ["daily", "weekly", "monthly", "yearly"]:
        raise ValueError(
            "Invalid billing cycle. Must be one of: daily, weekly, monthly, yearly."
        )

    if next_billing_date.tzinfo is None:
        next_billing_date = next_billing_date.replace(tzinfo=timezone.utc)

    if next_billing_date <= datetime.now(timezone.utc):
        raise ValueError("Next billing date must be in the future.")

    if next_billing_date_check <= datetime.now(timezone.utc).date():
        raise ValueError("Next billing date must be in the future.")

    # Identify which fields have changed and update only those to optimise database operations
    changed = False
    if subscription.name != name:
        subscription.name = name
        changed = True

    if subscription.amount != amount:
        subscription.amount = amount
        changed = True

    if subscription.billing_cycle != billing_cycle:
        subscription.billing_cycle = billing_cycle
        changed = True

    if subscription.next_billing_date != next_billing_date:
        subscription.next_billing_date = next_billing_date
        changed = True

    # If no changes were made, we can skip the database commit to save resources
    if changed:
        db.session.commit()
        db.session.refresh(subscription)

    return subscription


def deactivate_subscription(subscription):
    if subscription is None:
        raise ValueError("Subscription not found.")

    subscription.active = False
    db.session.commit()
    db.session.refresh(subscription)
    return subscription


def generate_due_expenses(today):

    due_subscriptions = Subscription.query.filter(
        Subscription.active == True, Subscription.next_billing_date <= today
    ).all()

    for sub in due_subscriptions:

        if sub.owner_type != "group":
            continue  # Skip non-group subscriptions for now

        group = Group.query.get(sub.owner_id)
        creator = User.query.get(sub.created_by)

        # Check if an expense has already been generated for this subscription and billing period
        billing_period = sub.next_billing_date.strftime("%m-%Y")
        existing = GeneratedExpense.query.filter_by(
            subscription_id=sub.id, billing_period=billing_period
        ).first()

        if existing:
            continue

        # Create expense using expense service
        expense = expense_service.create_expense(
            group=group,
            creator_user=creator,
            description=f"Subscription {sub.name}",
            total_amount=sub.amount,
            date=today,
            split_equally=True,
        )
        db.session.add(expense)
        db.session.flush()  # Flush to get expense ID for GeneratedExpense record

        # Record generated link
        generated = GeneratedExpense(
            subscription_id=sub.id,
            expense_id=expense.id,
            billing_period=sub.next_billing_date.strftime("%m-%Y"),
        )

        db.session.add(generated)

        # Advance billing date
        advance_billing_date(sub)

    db.session.commit()


def advance_billing_date(subscription):
    if subscription is None:
        raise ValueError("Subscription not found.")

    if subscription.billing_cycle == "daily":
        subscription.next_billing_date += timedelta(days=1)

    elif subscription.billing_cycle == "weekly":
        subscription.next_billing_date += timedelta(weeks=1)

    elif subscription.billing_cycle == "monthly":
        subscription.next_billing_date += relativedelta(months=1)

    elif subscription.billing_cycle == "yearly":
        subscription.next_billing_date += relativedelta(years=1)

    return subscription
