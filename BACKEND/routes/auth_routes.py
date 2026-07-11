"""
Authentication routes — Blueprint: 'auth'

Maps URLs to auth controller functions.
Routes contain no logic.
"""

from flask import Blueprint
from controllers.auth_controller import logout, process_login, show_login

auth_bp = Blueprint("auth", __name__)

auth_bp.add_url_rule("/",        "login_get",  show_login,     methods=["GET"])
auth_bp.add_url_rule("/login",   "login_get",  show_login,     methods=["GET"])
auth_bp.add_url_rule("/login",   "login_post", process_login,  methods=["POST"])
auth_bp.add_url_rule("/logout",  "logout",     logout,         methods=["GET"])
