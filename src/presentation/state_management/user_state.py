"""Re-export UserState from global_state for backward compatibility."""

from src.presentation.state_management.global_state import UserState

__all__ = ["UserState"]
