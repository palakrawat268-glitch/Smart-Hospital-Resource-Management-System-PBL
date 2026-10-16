# modules/module1_palak_auth/__init__.py
# Author: Palak Rawat
# OS Concept: Process Synchronization / Authentication State & Session Control

from .models import User
from .routes import auth_bp, dashboard_bp

__all__ = ['User', 'auth_bp', 'dashboard_bp']
