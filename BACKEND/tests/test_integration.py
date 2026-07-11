"""
Integration tests — Flask routes, controllers, services, and database
working together via the Flask test client.
"""


# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------

class TestLoginPage:

    def test_get_login_returns_200(self, test_client):
        response = test_client.get("/login")
        assert response.status_code == 200
        assert b"Sign In" in response.data

    def test_post_valid_credentials_redirects_to_dashboard(self, test_client):
        response = test_client.post(
            "/login",
            data={"username": "demo", "password": "password123"},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "/dashboard" in response.headers["Location"]

    def test_post_wrong_password_returns_error(self, test_client):
        response = test_client.post(
            "/login",
            data={"username": "demo", "password": "wrong"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Invalid username or password" in response.data

    def test_post_unknown_username_returns_error(self, test_client):
        response = test_client.post(
            "/login",
            data={"username": "nobody", "password": "anything"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Invalid username or password" in response.data

    def test_post_empty_fields_returns_error(self, test_client):
        response = test_client.post(
            "/login",
            data={"username": "", "password": ""},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Please enter your username and password" in response.data


class TestLogout:

    def test_logout_clears_session_and_redirects(self, test_client):
        # Log in first
        test_client.post(
            "/login",
            data={"username": "demo", "password": "password123"},
            follow_redirects=True,
        )
        # Now log out
        response = test_client.get("/logout", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.headers["Location"] or response.headers["Location"] == "/"


# ---------------------------------------------------------------------------
# Protected routes — unauthenticated access
# ---------------------------------------------------------------------------

class TestProtectedRoutes:

    def test_dashboard_without_session_redirects_to_login(self, test_client):
        response = test_client.get("/dashboard", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.headers["Location"] or response.headers["Location"] == "/"

    def test_deposit_without_session_redirects_to_login(self, test_client):
        response = test_client.get("/deposit", follow_redirects=False)
        assert response.status_code == 302

    def test_withdraw_without_session_redirects_to_login(self, test_client):
        response = test_client.get("/withdraw", follow_redirects=False)
        assert response.status_code == 302


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

class TestDashboard:

    def _login(self, client):
        client.post(
            "/login",
            data={"username": "demo", "password": "password123"},
            follow_redirects=True,
        )

    def test_dashboard_shows_balance(self, test_client):
        self._login(test_client)
        response = test_client.get("/dashboard")
        assert response.status_code == 200
        assert b"1000" in response.data  # seeded balance

    def test_dashboard_shows_customer_name(self, test_client):
        self._login(test_client)
        response = test_client.get("/dashboard")
        assert b"Alex Johnson" in response.data


# ---------------------------------------------------------------------------
# Deposit route
# ---------------------------------------------------------------------------

class TestDepositRoute:

    def _login(self, client):
        client.post(
            "/login",
            data={"username": "demo", "password": "password123"},
            follow_redirects=True,
        )

    def test_get_deposit_returns_200(self, test_client):
        self._login(test_client)
        response = test_client.get("/deposit")
        assert response.status_code == 200
        assert b"Deposit" in response.data

    def test_valid_deposit_redirects_to_dashboard(self, test_client):
        self._login(test_client)
        response = test_client.post(
            "/deposit", data={"amount": "500"}, follow_redirects=False
        )
        assert response.status_code == 302
        assert "/dashboard" in response.headers["Location"]

    def test_valid_deposit_updates_balance(self, test_client):
        self._login(test_client)
        test_client.post("/deposit", data={"amount": "500"}, follow_redirects=True)
        response = test_client.get("/dashboard")
        assert b"1500" in response.data

    def test_zero_deposit_returns_error(self, test_client):
        self._login(test_client)
        response = test_client.post(
            "/deposit", data={"amount": "0"}, follow_redirects=True
        )
        assert response.status_code == 200
        assert b"greater than zero" in response.data

    def test_non_numeric_deposit_returns_error(self, test_client):
        self._login(test_client)
        response = test_client.post(
            "/deposit", data={"amount": "abc"}, follow_redirects=True
        )
        assert response.status_code == 200
        assert b"number" in response.data

    def test_empty_deposit_returns_error(self, test_client):
        self._login(test_client)
        response = test_client.post(
            "/deposit", data={"amount": ""}, follow_redirects=True
        )
        assert response.status_code == 200
        assert b"enter an amount" in response.data


# ---------------------------------------------------------------------------
# Withdraw route
# ---------------------------------------------------------------------------

class TestWithdrawRoute:

    def _login(self, client):
        client.post(
            "/login",
            data={"username": "demo", "password": "password123"},
            follow_redirects=True,
        )

    def test_get_withdraw_returns_200(self, test_client):
        self._login(test_client)
        response = test_client.get("/withdraw")
        assert response.status_code == 200
        assert b"Withdraw" in response.data

    def test_valid_withdrawal_redirects_to_dashboard(self, test_client):
        self._login(test_client)
        response = test_client.post(
            "/withdraw", data={"amount": "200"}, follow_redirects=False
        )
        assert response.status_code == 302
        assert "/dashboard" in response.headers["Location"]

    def test_valid_withdrawal_updates_balance(self, test_client):
        self._login(test_client)
        test_client.post("/withdraw", data={"amount": "200"}, follow_redirects=True)
        response = test_client.get("/dashboard")
        assert b"800" in response.data

    def test_overdraft_returns_error(self, test_client):
        self._login(test_client)
        response = test_client.post(
            "/withdraw", data={"amount": "9999"}, follow_redirects=True
        )
        assert response.status_code == 200
        assert b"Insufficient funds" in response.data

    def test_zero_withdrawal_returns_error(self, test_client):
        self._login(test_client)
        response = test_client.post(
            "/withdraw", data={"amount": "0"}, follow_redirects=True
        )
        assert response.status_code == 200
        assert b"greater than zero" in response.data
