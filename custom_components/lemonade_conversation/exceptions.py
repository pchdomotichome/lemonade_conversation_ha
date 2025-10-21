"""Exceptions for Lemonade Conversation integration."""
from homeassistant.exceptions import HomeAssistantError


class LemonadeException(HomeAssistantError):
    """Base exception for Lemonade integration."""


class LemonadeConnectionError(LemonadeException):
    """Exception raised when connection to Lemonade server fails."""


class LemonadeTimeoutError(LemonadeException):
    """Exception raised when request to Lemonade server times out."""


class LemonadeAPIError(LemonadeException):
    """Exception raised when Lemonade API returns an error."""


class LemonadeModelNotFoundError(LemonadeException):
    """Exception raised when requested model is not available."""


class LemonadeInvalidResponseError(LemonadeException):
    """Exception raised when Lemonade returns invalid response."""


class LemonadeConfigurationError(LemonadeException):
    """Exception raised when configuration is invalid."""
