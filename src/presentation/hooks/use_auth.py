"""Hook for GitHub authentication — bridges UserState with auth operations."""

from src.presentation.state_management.global_state import UserState


def is_authenticated(user: UserState) -> bool:
    return user.is_authenticated and bool(user.github_token)
