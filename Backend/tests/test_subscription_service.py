import unittest
from decimal import Decimal
from datetime import datetime, timezone, timedelta, date
from dateutil.relativedelta import relativedelta

from app import create_app
from app.extensions import db
from app.models import User, Group, Subscription, GeneratedExpense, Expense
from app.services import subscription_service


class TestSubscriptionService(unittest.TestCase):
    """Test suite for subscription service logic"""

    def setUp(self):
        """Set up test fixtures before each test"""
        self.app = create_app()
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["TESTING"] = True

        with self.app.app_context():
            db.create_all()

            # Create test users
            user1 = User(name="Alice", email="alice@test.com", password_hash="hash1")
            user2 = User(name="Bob", email="bob@test.com", password_hash="hash2")
            db.session.add_all([user1, user2])
            db.session.commit()

            self.user1_id = user1.id
            self.user2_id = user2.id

            # Create test group
            group = Group(
                name="Test Group",
                description="Test group for subscriptions",
                created_by=user1.id,
            )
            db.session.add(group)
            db.session.commit()

            self.group_id = group.id

    def tearDown(self):
        """Clean up after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    # ========== CREATE SUBSCRIPTION TESTS ==========

    def test_create_subscription_success_user_type(self):
        """Test creating a valid user subscription"""
        with self.app.app_context():
            future_date = datetime.now(timezone.utc) + timedelta(days=7)

            subscription = subscription_service.create_subscription(
                name="Netflix",
                amount=Decimal("12.99"),
                billing_cycle="monthly",
                next_billing_date=future_date,
                owner_type="user",
                owner_id=self.user1_id,
                created_by=self.user1_id,
            )

            self.assertIsNotNone(subscription.id)
            self.assertEqual(subscription.name, "Netflix")
            self.assertEqual(subscription.amount, Decimal("12.99"))
            self.assertEqual(subscription.billing_cycle, "monthly")
            self.assertEqual(subscription.owner_type, "user")
            self.assertTrue(subscription.active)

    def test_create_subscription_success_group_type(self):
        """Test creating a valid group subscription"""
        with self.app.app_context():
            future_date = datetime.now(timezone.utc) + timedelta(days=7)

            subscription = subscription_service.create_subscription(
                name="Spotify Family",
                amount=Decimal("15.99"),
                billing_cycle="monthly",
                next_billing_date=future_date,
                owner_type="group",
                owner_id=self.group_id,
                created_by=self.user1_id,
            )

            self.assertIsNotNone(subscription.id)
            self.assertEqual(subscription.owner_type, "group")
            self.assertEqual(subscription.owner_id, self.group_id)

    def test_create_subscription_invalid_amount_zero(self):
        """Test that amount must be greater than zero"""
        with self.app.app_context():
            future_date = datetime.now(timezone.utc) + timedelta(days=7)

            with self.assertRaises(ValueError) as context:
                subscription_service.create_subscription(
                    name="Invalid",
                    amount=Decimal("0"),
                    billing_cycle="monthly",
                    next_billing_date=future_date,
                    owner_type="user",
                    owner_id=self.user1_id,
                    created_by=self.user1_id,
                )

            self.assertIn("greater than zero", str(context.exception))

    def test_create_subscription_invalid_amount_negative(self):
        """Test that amount cannot be negative"""
        with self.app.app_context():
            future_date = datetime.now(timezone.utc) + timedelta(days=7)

            with self.assertRaises(ValueError) as context:
                subscription_service.create_subscription(
                    name="Invalid",
                    amount=Decimal("-10.00"),
                    billing_cycle="monthly",
                    next_billing_date=future_date,
                    owner_type="user",
                    owner_id=self.user1_id,
                    created_by=self.user1_id,
                )

            self.assertIn("greater than zero", str(context.exception))

    def test_create_subscription_invalid_billing_cycle(self):
        """Test that billing cycle must be valid"""
        with self.app.app_context():
            future_date = datetime.now(timezone.utc) + timedelta(days=7)

            with self.assertRaises(ValueError) as context:
                subscription_service.create_subscription(
                    name="Invalid",
                    amount=Decimal("10.00"),
                    billing_cycle="hourly",  # Invalid
                    next_billing_date=future_date,
                    owner_type="user",
                    owner_id=self.user1_id,
                    created_by=self.user1_id,
                )

            self.assertIn("Invalid billing cycle", str(context.exception))

    def test_create_subscription_past_billing_date(self):
        """Test that next billing date must be in the future"""
        with self.app.app_context():
            past_date = datetime.now(timezone.utc) - timedelta(days=1)

            with self.assertRaises(ValueError) as context:
                subscription_service.create_subscription(
                    name="Invalid",
                    amount=Decimal("10.00"),
                    billing_cycle="monthly",
                    next_billing_date=past_date,
                    owner_type="user",
                    owner_id=self.user1_id,
                    created_by=self.user1_id,
                )

            self.assertIn("must be in the future", str(context.exception))

    def test_create_subscription_invalid_owner_type(self):
        """Test that owner type must be 'user' or 'group'"""
        with self.app.app_context():
            future_date = datetime.now(timezone.utc) + timedelta(days=7)

            with self.assertRaises(ValueError) as context:
                subscription_service.create_subscription(
                    name="Invalid",
                    amount=Decimal("10.00"),
                    billing_cycle="monthly",
                    next_billing_date=future_date,
                    owner_type="company",  # Invalid
                    owner_id=self.user1_id,
                    created_by=self.user1_id,
                )

            self.assertIn("Invalid owner type", str(context.exception))

    def test_create_subscription_missing_owner_id(self):
        """Test that owner ID must be provided"""
        with self.app.app_context():
            future_date = datetime.now(timezone.utc) + timedelta(days=7)

            with self.assertRaises(ValueError) as context:
                subscription_service.create_subscription(
                    name="Invalid",
                    amount=Decimal("10.00"),
                    billing_cycle="monthly",
                    next_billing_date=future_date,
                    owner_type="user",
                    owner_id=None,  # Missing
                    created_by=self.user1_id,
                )

            self.assertIn("Owner ID must be provided", str(context.exception))

    # ========== UPDATE SUBSCRIPTION TESTS ==========

    def test_update_subscription_success(self):
        """Test updating a subscription successfully"""
        with self.app.app_context():
            # Create initial subscription
            future_date = date.today() + timedelta(days=7)
            subscription = Subscription(
                name="Netflix",
                amount=Decimal("12.99"),
                billing_cycle="monthly",
                next_billing_date=future_date,
                owner_type="user",
                owner_id=self.user1_id,
                created_by=self.user1_id,
            )
            db.session.add(subscription)
            db.session.commit()

            # Update it
            new_date = date.today() + timedelta(days=14)
            updated = subscription_service.update_subscription(
                subscription=subscription,
                name="Netflix Premium",
                amount=Decimal("15.99"),
                billing_cycle="yearly",
                next_billing_date=new_date,
            )

            self.assertEqual(updated.name, "Netflix Premium")
            self.assertEqual(updated.amount, Decimal("15.99"))
            self.assertEqual(updated.billing_cycle, "yearly")

    def test_update_subscription_none(self):
        """Test updating a None subscription raises error"""
        with self.app.app_context():
            future_date = datetime.now(timezone.utc) + timedelta(days=7)

            with self.assertRaises(ValueError) as context:
                subscription_service.update_subscription(
                    subscription=None,
                    name="Test",
                    amount=Decimal("10.00"),
                    billing_cycle="monthly",
                    next_billing_date=future_date,
                )

            self.assertIn("Subscription not found", str(context.exception))

    def test_update_subscription_no_changes(self):
        """Test that no database commit happens if nothing changes"""
        with self.app.app_context():
            future_date = date.today() + timedelta(days=7)
            subscription = Subscription(
                name="Netflix",
                amount=Decimal("12.99"),
                billing_cycle="monthly",
                next_billing_date=future_date,
                owner_type="user",
                owner_id=self.user1_id,
                created_by=self.user1_id,
            )
            db.session.add(subscription)
            db.session.commit()

            # Update with same values
            updated = subscription_service.update_subscription(
                subscription=subscription,
                name="Netflix",
                amount=Decimal("12.99"),
                billing_cycle="monthly",
                next_billing_date=future_date,
            )

            # Should return the subscription unchanged
            self.assertEqual(updated.name, "Netflix")

    # ========== DEACTIVATE SUBSCRIPTION TESTS ==========

    def test_deactivate_subscription_success(self):
        """Test deactivating a subscription"""
        with self.app.app_context():
            future_date = date.today() + timedelta(days=7)
            subscription = Subscription(
                name="Netflix",
                amount=Decimal("12.99"),
                billing_cycle="monthly",
                next_billing_date=future_date,
                owner_type="user",
                owner_id=self.user1_id,
                created_by=self.user1_id,
                active=True,
            )
            db.session.add(subscription)
            db.session.commit()

            # Deactivate
            result = subscription_service.deactivate_subscription(subscription)

            self.assertFalse(result.active)

    def test_deactivate_subscription_none(self):
        """Test deactivating a None subscription raises error"""
        with self.app.app_context():
            with self.assertRaises(ValueError) as context:
                subscription_service.deactivate_subscription(None)

            self.assertIn("Subscription not found", str(context.exception))

    # ========== ADVANCE BILLING DATE TESTS ==========

    def test_advance_billing_date_daily(self):
        """Test advancing billing date for daily subscription"""
        with self.app.app_context():
            start_date = date(2026, 2, 10)
            subscription = Subscription(
                name="Daily Sub",
                amount=Decimal("1.00"),
                billing_cycle="daily",
                next_billing_date=start_date,
                owner_type="user",
                owner_id=self.user1_id,
                created_by=self.user1_id,
            )
            db.session.add(subscription)
            db.session.commit()

            subscription_service.advance_billing_date(subscription)

            expected_date = start_date + timedelta(days=1)
            self.assertEqual(subscription.next_billing_date, expected_date)

    def test_advance_billing_date_weekly(self):
        """Test advancing billing date for weekly subscription"""
        with self.app.app_context():
            start_date = date(2026, 2, 10)
            subscription = Subscription(
                name="Weekly Sub",
                amount=Decimal("10.00"),
                billing_cycle="weekly",
                next_billing_date=start_date,
                owner_type="user",
                owner_id=self.user1_id,
                created_by=self.user1_id,
            )
            db.session.add(subscription)
            db.session.commit()

            subscription_service.advance_billing_date(subscription)

            expected_date = start_date + timedelta(weeks=1)
            self.assertEqual(subscription.next_billing_date, expected_date)

    def test_advance_billing_date_monthly(self):
        """Test advancing billing date for monthly subscription"""
        with self.app.app_context():
            start_date = date(2026, 2, 10)
            subscription = Subscription(
                name="Monthly Sub",
                amount=Decimal("10.00"),
                billing_cycle="monthly",
                next_billing_date=start_date,
                owner_type="user",
                owner_id=self.user1_id,
                created_by=self.user1_id,
            )
            db.session.add(subscription)
            db.session.commit()

            subscription_service.advance_billing_date(subscription)

            expected_date = start_date + relativedelta(months=1)
            self.assertEqual(subscription.next_billing_date, expected_date)

    def test_advance_billing_date_yearly(self):
        """Test advancing billing date for yearly subscription"""
        with self.app.app_context():
            start_date = date(2026, 2, 10)
            subscription = Subscription(
                name="Yearly Sub",
                amount=Decimal("100.00"),
                billing_cycle="yearly",
                next_billing_date=start_date,
                owner_type="user",
                owner_id=self.user1_id,
                created_by=self.user1_id,
            )
            db.session.add(subscription)
            db.session.commit()

            subscription_service.advance_billing_date(subscription)

            expected_date = start_date + relativedelta(years=1)
            self.assertEqual(subscription.next_billing_date, expected_date)

    def test_advance_billing_date_none(self):
        """Test advancing billing date for None subscription raises error"""
        with self.app.app_context():
            with self.assertRaises(ValueError) as context:
                subscription_service.advance_billing_date(None)

            self.assertIn("Subscription not found", str(context.exception))


if __name__ == "__main__":
    unittest.main()
