class NoFangraphsIdError(Exception):
    """Raised when create_from_mlb returns None."""
    pass

class PlayerNotFoundError(Exception):
    """Raised when create_from_mlb returns None."""
    pass

class PositionMismatchError(Exception):
    """Raised when a player does not match the requested pitcher/batter filter."""
    pass

class NoStatsError(Exception):
    """Raised when stats are fetched but empty."""
    pass

class StatFetchError(Exception):
    """Wraps any unexpected exception during stats fetching."""
    pass