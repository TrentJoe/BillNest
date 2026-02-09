import unittest
from decimal import Decimal
from collections import defaultdict
from datetime import datetime

from app import create_app
from app.extensions import db
from app.models import User, Group, Expense, ExpenseSplit, Settlement
from app.services.balance_service import calculate_group_balances


class TestBalanceService(unittest.TestCase):
    """Test suite for balance calculation logic"""
    
    def setUp(self):
        """Set up test fixtures before each test"""
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['TESTING'] = True
        
        with self.app.app_context():
            db.create_all()
            
            # Create test users
            alice = User(name="Alice", email="alice@test.com", password_hash="hash1")
            bob = User(name="Bob", email="bob@test.com", password_hash="hash2")
            carol = User(name="Carol", email="carol@test.com", password_hash="hash3")
            
            db.session.add_all([alice, bob, carol])
            db.session.commit()
            
            # Store IDs for use in tests
            self.alice_id = alice.id
            self.bob_id = bob.id
            self.carol_id = carol.id
            
            # Create test group
            group = Group(
                name="Test Group",
                description="Test group for balance calculations",
                created_by=alice.id
            )
            db.session.add(group)
            db.session.commit()
            
            # Store group ID
            self.group_id = group.id
    
    def tearDown(self):
        """Clean up after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_empty_group_has_zero_balances(self):
        """Test that a group with no expenses has zero balances"""
        with self.app.app_context():
            group = Group.query.get(self.group_id)
            balances = calculate_group_balances(group)
            
            # Should return empty dict or all zeros
            self.assertEqual(len(balances), 0)
    
    def test_single_expense_even_split(self):
        """Test a single expense split evenly among three people"""
        with self.app.app_context():
            # Alice pays £60 for dinner
            expense = Expense(
                group_id=self.group_id,
                created_by=self.alice_id,
                description="Dinner",
                total_amount=Decimal("60.00"),
                date=datetime(2026, 2, 5)
            )
            db.session.add(expense)
            db.session.commit()
            
            # Split evenly: £20 each
            splits = [
                ExpenseSplit(expense_id=expense.id, user_id=self.alice_id, amount_owed=Decimal("20.00")),
                ExpenseSplit(expense_id=expense.id, user_id=self.bob_id, amount_owed=Decimal("20.00")),
                ExpenseSplit(expense_id=expense.id, user_id=self.carol_id, amount_owed=Decimal("20.00"))
            ]
            db.session.add_all(splits)
            db.session.commit()
            
            # Calculate balances
            group = Group.query.get(self.group_id)
            balances = calculate_group_balances(group)
            
            # Alice paid £60 but owes £20, so she's owed £40
            self.assertEqual(balances[self.alice_id], Decimal("40.00"))
            # Bob owes £20
            self.assertEqual(balances[self.bob_id], Decimal("-20.00"))
            # Carol owes £20
            self.assertEqual(balances[self.carol_id], Decimal("-20.00"))
            
            # Total should sum to zero
            total = sum(balances.values())
            self.assertEqual(total, Decimal("0.00"))
    
    def test_single_expense_uneven_split(self):
        """Test a single expense with uneven splits"""
        with self.app.app_context():
            # Bob pays £100 for groceries
            expense = Expense(
                group_id=self.group_id,
                created_by=self.bob_id,
                description="Groceries",
                total_amount=Decimal("100.00"),
                date=datetime(2026, 2, 5)
            )
            db.session.add(expense)
            db.session.commit()
            
            # Uneven split based on who ate what
            splits = [
                ExpenseSplit(expense_id=expense.id, user_id=self.alice_id, amount_owed=Decimal("30.00")),
                ExpenseSplit(expense_id=expense.id, user_id=self.bob_id, amount_owed=Decimal("45.00")),
                ExpenseSplit(expense_id=expense.id, user_id=self.carol_id, amount_owed=Decimal("25.00"))
            ]
            db.session.add_all(splits)
            db.session.commit()
            
            # Calculate balances
            group = Group.query.get(self.group_id)
            balances = calculate_group_balances(group)
            
            # Alice owes £30
            self.assertEqual(balances[self.alice_id], Decimal("-30.00"))
            # Bob paid £100 but owes £45, so he's owed £55
            self.assertEqual(balances[self.bob_id], Decimal("55.00"))
            # Carol owes £25
            self.assertEqual(balances[self.carol_id], Decimal("-25.00"))
            
            # Total should sum to zero
            total = sum(balances.values())
            self.assertEqual(total, Decimal("0.00"))
    
    def test_multiple_expenses(self):
        """Test multiple expenses with different payers"""
        with self.app.app_context():
            # Expense 1: Alice pays £60
            expense1 = Expense(
                group_id=self.group_id,
                created_by=self.alice_id,
                description="Dinner",
                total_amount=Decimal("60.00"),
                date=datetime(2026, 2, 5)
            )
            db.session.add(expense1)
            db.session.commit()
            
            splits1 = [
                ExpenseSplit(expense_id=expense1.id, user_id=self.alice_id, amount_owed=Decimal("20.00")),
                ExpenseSplit(expense_id=expense1.id, user_id=self.bob_id, amount_owed=Decimal("20.00")),
                ExpenseSplit(expense_id=expense1.id, user_id=self.carol_id, amount_owed=Decimal("20.00"))
            ]
            db.session.add_all(splits1)
            db.session.commit()
            
            # Expense 2: Bob pays £30
            expense2 = Expense(
                group_id=self.group_id,
                created_by=self.bob_id,
                description="Coffee",
                total_amount=Decimal("30.00"),
                date=datetime(2026, 2, 5)
            )
            db.session.add(expense2)
            db.session.commit()
            
            splits2 = [
                ExpenseSplit(expense_id=expense2.id, user_id=self.alice_id, amount_owed=Decimal("10.00")),
                ExpenseSplit(expense_id=expense2.id, user_id=self.bob_id, amount_owed=Decimal("10.00")),
                ExpenseSplit(expense_id=expense2.id, user_id=self.carol_id, amount_owed=Decimal("10.00"))
            ]
            db.session.add_all(splits2)
            db.session.commit()
            
            # Calculate balances
            group = Group.query.get(self.group_id)
            balances = calculate_group_balances(group)
            
            # Alice: paid £60, owes £30 (20+10) = +£30
            self.assertEqual(balances[self.alice_id], Decimal("30.00"))
            # Bob: paid £30, owes £30 (20+10) = £0
            self.assertEqual(balances[self.bob_id], Decimal("0.00"))
            # Carol: paid £0, owes £30 (20+10) = -£30
            self.assertEqual(balances[self.carol_id], Decimal("-30.00"))
            
            # Total should sum to zero
            total = sum(balances.values())
            self.assertEqual(total, Decimal("0.00"))
    
    def test_confirmed_settlement_reduces_balance(self):
        """Test that confirmed settlements reduce balances"""
        with self.app.app_context():
            # Alice pays £60, split evenly
            expense = Expense(
                group_id=self.group_id,
                created_by=self.alice_id,
                description="Dinner",
                total_amount=Decimal("60.00"),
                date=datetime(2026, 2, 5)
            )
            db.session.add(expense)
            db.session.commit()
            
            splits = [
                ExpenseSplit(expense_id=expense.id, user_id=self.alice_id, amount_owed=Decimal("20.00")),
                ExpenseSplit(expense_id=expense.id, user_id=self.bob_id, amount_owed=Decimal("20.00")),
                ExpenseSplit(expense_id=expense.id, user_id=self.carol_id, amount_owed=Decimal("20.00"))
            ]
            db.session.add_all(splits)
            db.session.commit()
            
            # Bob pays Alice back £20 (confirmed)
            settlement = Settlement(
                group_id=self.group_id,
                from_user_id=self.bob_id,
                to_user_id=self.alice_id,
                amount=Decimal("20.00"),
                status="confirmed"
            )
            db.session.add(settlement)
            db.session.commit()
            
            # Calculate balances
            group = Group.query.get(self.group_id)
            balances = calculate_group_balances(group)
            
            # Alice: owed £40, received £20 = now owed £20
            self.assertEqual(balances[self.alice_id], Decimal("20.00"))
            # Bob: owed -£20, paid £20 = now £0
            self.assertEqual(balances[self.bob_id], Decimal("0.00"))
            # Carol: still owes £20
            self.assertEqual(balances[self.carol_id], Decimal("-20.00"))
            
            # Total should sum to zero
            total = sum(balances.values())
            self.assertEqual(total, Decimal("0.00"))
    
    def test_pending_settlement_ignored(self):
        """Test that pending settlements are not included in balance calculation"""
        with self.app.app_context():
            # Alice pays £60, split evenly
            expense = Expense(
                group_id=self.group_id,
                created_by=self.alice_id,
                description="Dinner",
                total_amount=Decimal("60.00"),
                date=datetime(2026, 2, 5)
            )
            db.session.add(expense)
            db.session.commit()
            
            splits = [
                ExpenseSplit(expense_id=expense.id, user_id=self.alice_id, amount_owed=Decimal("20.00")),
                ExpenseSplit(expense_id=expense.id, user_id=self.bob_id, amount_owed=Decimal("20.00")),
                ExpenseSplit(expense_id=expense.id, user_id=self.carol_id, amount_owed=Decimal("20.00"))
            ]
            db.session.add_all(splits)
            db.session.commit()
            
            # Bob says he'll pay Alice back £20 (pending - not confirmed yet)
            settlement = Settlement(
                group_id=self.group_id,
                from_user_id=self.bob_id,
                to_user_id=self.alice_id,
                amount=Decimal("20.00"),
                status="pending"
            )
            db.session.add(settlement)
            db.session.commit()
            
            # Calculate balances
            group = Group.query.get(self.group_id)
            balances = calculate_group_balances(group)
            
            # Pending settlement should be ignored
            # Alice: still owed £40
            self.assertEqual(balances[self.alice_id], Decimal("40.00"))
            # Bob: still owes £20
            self.assertEqual(balances[self.bob_id], Decimal("-20.00"))
            # Carol: still owes £20
            self.assertEqual(balances[self.carol_id], Decimal("-20.00"))


if __name__ == '__main__':
    unittest.main()

