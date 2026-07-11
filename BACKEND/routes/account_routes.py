"""
Account routes — Blueprint: 'account'

Maps URLs to account controller functions.
Routes contain no logic.
"""

from flask import Blueprint
from controllers.account_controller import (
    process_deposit,
    process_withdraw,
    show_dashboard,
    show_deposit,
    show_withdraw,
)

account_bp = Blueprint("account", __name__)

account_bp.add_url_rule("/dashboard", "dashboard",       show_dashboard,  methods=["GET"])
account_bp.add_url_rule("/deposit",   "deposit_get",     show_deposit,    methods=["GET"])
account_bp.add_url_rule("/deposit",   "deposit_post",    process_deposit, methods=["POST"])
account_bp.add_url_rule("/withdraw",  "withdraw_get",    show_withdraw,   methods=["GET"])
account_bp.add_url_rule("/withdraw",  "withdraw_post",   process_withdraw, methods=["POST"])
