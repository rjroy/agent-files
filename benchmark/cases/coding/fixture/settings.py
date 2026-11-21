"""Resolve the weekly digest preference for one workspace."""


def effective_enabled(settings, default):
    """Return the workspace preference or the application default."""
    return settings.get("enabled") or default
