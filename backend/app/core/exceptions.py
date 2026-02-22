"""
Custom exceptions for the application
"""
from typing import Any, Optional

class BaseAppException(Exception):
    """Base exception for application-specific exceptions"""
    def __init__(self, message: str, details: Optional[Any] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)

class AIProcessingError(BaseAppException):
    """Raised when AI processing fails"""
    pass

class DocumentProcessingError(BaseAppException):
    """Raised when document processing fails"""
    pass

class ValidationError(BaseAppException):
    """Raised when data validation fails"""
    pass

class ResourceNotFoundError(BaseAppException):
    """Raised when a requested resource is not found"""
    pass

class AuthenticationError(BaseAppException):
    """Raised when authentication fails"""
    pass

class AuthorizationError(BaseAppException):
    """Raised when user is not authorized to perform an action"""
    pass

class RateLimitExceededError(BaseAppException):
    """Raised when rate limit is exceeded"""
    pass

class CacheError(BaseAppException):
    """Raised when cache operations fail"""
    pass

class ConfigurationError(BaseAppException):
    """Raised when there's a configuration error"""
    pass

class ExternalServiceError(BaseAppException):
    """Raised when an external service call fails"""
    pass

class DatabaseError(BaseAppException):
    """Raised when database operations fail"""
    pass

class FileOperationError(BaseAppException):
    """Raised when file operations fail"""
    pass