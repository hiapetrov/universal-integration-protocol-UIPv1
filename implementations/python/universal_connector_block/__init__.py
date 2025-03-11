"""
Universal Connector Block (UCB) Reference Implementation for Python

This module provides a Python implementation of the Universal Connector Block
as defined in the Universal Integration Protocol specification.
"""

__version__ = "0.1.0"

from .core import UniversalConnectorBlock
from .errors import UcbError, ValidationError
from .enums import HttpMethod, AuthMethod, ParameterLocation
from .types import TypeMapper, register_type_adapter
from .resilience import CircuitBreaker, RateLimiter, Cacher

__all__ = [
    "UniversalConnectorBlock",
    "UcbError",
    "ValidationError",
    "HttpMethod",
    "AuthMethod",
    "ParameterLocation",
    "TypeMapper",
    "register_type_adapter",
    "CircuitBreaker",
    "RateLimiter",
    "Cacher",
]
