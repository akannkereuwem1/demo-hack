"""
Payment permissions.

Re-exports IsBuyer from users.permissions to keep imports explicit
within the payments app without duplicating logic.
"""

from users.permissions import IsBuyer  # noqa: F401
