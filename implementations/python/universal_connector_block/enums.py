"""
Enumerations used in the Universal Connector Block implementation.
"""

from enum import Enum


class AuthMethod(Enum):
    """Authentication methods supported by UCB."""
    NONE = "none"
    API_KEY = "api_key"
    BEARER = "bearer"
    BASIC = "basic"
    OAUTH2 = "oauth2"
    CUSTOM = "custom"


class ParameterLocation(Enum):
    """Possible locations for API parameters."""
    PATH = "path"
    QUERY = "query"
    HEADER = "header"
    BODY = "body"


class HttpMethod(Enum):
    """HTTP methods supported for endpoints."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"
