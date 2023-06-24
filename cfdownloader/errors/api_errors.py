class ApiKeyError(Exception):
    """Raised when the API key is invalid or missing."""
    pass


class GetModError(Exception):
    """Raised when the mod cannot be found."""
    pass
