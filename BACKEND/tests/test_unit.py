"""
Unit tests for auth_service and account_service.

These tests exercise service logic in isolation using the
in-memory database provided by the patch_db fixture in conftest.py.

Every test method must list patch_db as a parameter so pytest creates
a brand-new isolated in-memory database for each individual test.
"""

import pytest
from services.auth_service import verify_credentials
from services.account_service import deposit, get_balance, withdraw


# ---------------------------------------------------------------------------
# auth_service — verify_credentials
# ---------------------------------------------------------------------------

class TestVerifyCredentials:

    def test_valid_credentials_return_customer(self, patch_db):
        customer = verify_credentials("demo", "password123")
        assert customer is not None
        assert customer["username"] == "demo"
        assert customer["name"] == "Alex Johnson"

    def test_wrong_password_returns_none(self, patch_db):
        result = verify_credentials("demo", "wrongpassword")
        assert result is None

    def test_unknown_username_returns_none(self, patch_db):
        result = verify_credentials("nobody", "password123")
        assert result is None

    def test_empty_username_returns_none(self, patch_db):
        result = verify_credentials("", "password123")
        assert result is None

    def test_empty_password_returns_none(self, patch_db):
        result = verify_credentials("demo", "")
        assert result is None


# ---------------------------------------------------------------------------
# account_service — get_balance
# ---------------------------------------------------------------------------

class TestGetBalance:

    def test_returns_seeded_balance(self, patch_db):
        balance = get_balance(customer_id=1)
        assert balance == pytest.approx(1000.00)

    def test_raises_for_unknown_customer(self, patch_db):
        with pytest.raises(RuntimeError):
            get_balance(customer_id=999)


# ---------------------------------------------------------------------------
# account_service — deposit
# ---------------------------------------------------------------------------

class TestDeposit:

    def test_balance_increases_by_deposit_amount(self, patch_db):
        new_balance = deposit(customer_id=1, amount=500.00)
        assert new_balance == pytest.approx(1500.00)

    def test_balance_persisted_after_deposit(self, patch_db):
        deposit(customer_id=1, amount=250.00)
        balance = get_balance(customer_id=1)
        assert balance == pytest.approx(1250.00)

    def test_transaction_record_created_on_deposit(self, patch_db):
        deposit(customer_id=1, amount=100.00)
        row = patch_db.execute(
            "SELECT * FROM transactions WHERE customer_id=1 AND type='deposit'"
        ).fetchone()
        assert row is not None
        assert row["amount"] == pytest.approx(100.00)

    def test_zero_amount_raises(self, patch_db):
        with pytest.raises(ValueError):
            deposit(customer_id=1, amount=0)

    def test_negative_amount_raises(self, patch_db):
        with pytest.raises(ValueError):
            deposit(customer_id=1, amount=-50)


# ---------------------------------------------------------------------------
# account_service — withdraw
# ---------------------------------------------------------------------------

class TestWithdraw:

    def test_balance_decreases_by_withdrawal_amount(self, patch_db):
        new_balance = withdraw(customer_id=1, amount=200.00)
        assert new_balance == pytest.approx(800.00)

    def test_balance_persisted_after_withdrawal(self, patch_db):
        withdraw(customer_id=1, amount=300.00)
        balance = get_balance(customer_id=1)
        assert balance == pytest.approx(700.00)

    def test_transaction_record_created_on_withdrawal(self, patch_db):
        withdraw(customer_id=1, amount=50.00)
        row = patch_db.execute(
            "SELECT * FROM transactions WHERE customer_id=1 AND type='withdrawal'"
        ).fetchone()
        assert row is not None
        assert row["amount"] == pytest.approx(50.00)

    def test_overdraft_raises_value_error(self, patch_db):
        with pytest.raises(ValueError, match="Insufficient funds"):
            withdraw(customer_id=1, amount=9999.00)

    def test_exact_balance_withdrawal_succeeds(self, patch_db):
        new_balance = withdraw(customer_id=1, amount=1000.00)
        assert new_balance == pytest.approx(0.00)

    def test_zero_amount_raises(self, patch_db):
        with pytest.raises(ValueError):
            withdraw(customer_id=1, amount=0)

    def test_negative_amount_raises(self, patch_db):
        with pytest.raises(ValueError):
            withdraw(customer_id=1, amount=-100)
