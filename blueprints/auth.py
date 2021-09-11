from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    current_user
)
from extensions import db
from models.user import User
from datetime import timedelta

auth_bp = Blueprint('auth', __name__)
