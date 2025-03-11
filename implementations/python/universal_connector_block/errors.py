"""
Error classes for the Universal Connector Block implementation.
"""

import json
import uuid
import datetime
from typing import Dict, Any, List, Optional


class UcbError(Exception):
    """Base exception class for UCB errors."""
    
    def __init__(self, 
                 error_code: str, 
                 message: str, 
                 details: Optional[List[Dict[str, Any]]] = None,
                 status_code: int = 400):
        self.error_code = error_code
        self.message = message
        self.details = details or []
        self.status_code = status_code
        self.request_id = str(uuid.uuid4())
        self.timestamp = datetime.datetime.utcnow().isoformat()
        super().__init__(message)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary representation."""
        return {
            "errorCode": self.error_code,
            "message": self.message,
            "details": self.details,
            "requestId": self.request_id,
            "timestamp": self.timestamp
        }
        
    def to_json(self) -> str:
        """Convert error to JSON representation."""
        return json.dumps(self.to_dict())


class ValidationError(UcbError):
    """Error raised when input validation fails."""
    
    def __init__(self, message: str, details: List[Dict[str, Any]]):
        super().__init__("VALIDATION_ERROR", message, details)


class AuthenticationError(UcbError):
    """Error raised when authentication fails."""
    
    def __init__(self, message: str, details: Optional[List[Dict[str, Any]]] = None):
        super().__init__("AUTHENTICATION_ERROR", message, details, 401)


class AuthorizationError(UcbError):
    """Error raised when authorization fails."""
    
    def __init__(self, message: str, details: Optional[List[Dict[str, Any]]] = None):
        super().__init__("AUTHORIZATION_ERROR", message, details, 403)


class ResourceNotFoundError(UcbError):
    """Error raised when a requested resource is not found."""
    
    def __init__(self, message: str, details: Optional[List[Dict[str, Any]]] = None):
        super().__init__("RESOURCE_NOT_FOUND", message, details, 404)


class RateLimitExceededError(UcbError):
    """Error raised when rate limits are exceeded."""
    
    def __init__(self, message: str, details: Optional[List[Dict[str, Any]]] = None):
        super().__init__("RATE_LIMIT_EXCEEDED", message, details, 429)


class ConnectionError(UcbError):
    """Error raised when connection to an external service fails."""
    
    def __init__(self, message: str, details: Optional[List[Dict[str, Any]]] = None):
        super().__init__("CONNECTION_ERROR", message, details, 503)


class TimeoutError(UcbError):
    """Error raised when a request times out."""
    
    def __init__(self, message: str, details: Optional[List[Dict[str, Any]]] = None):
        super().__init__("TIMEOUT_ERROR", message, details, 504)
