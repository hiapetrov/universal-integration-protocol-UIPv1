"""
Data models for the Universal Connector Block implementation.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Callable

from .enums import HttpMethod, AuthMethod, ParameterLocation


@dataclass
class Parameter:
    """Parameter description for API endpoints."""
    name: str
    type: str
    location: ParameterLocation
    required: bool = True
    description: Optional[str] = None
    default_value: Optional[Any] = None


@dataclass
class Response:
    """Response description for API endpoints."""
    status_code: int
    content_type: str = "application/json"
    schema: Optional[Dict[str, Any]] = None
    description: Optional[str] = None


@dataclass
class Endpoint:
    """API endpoint description."""
    path: str
    method: HttpMethod
    handler: Callable
    parameters: List[Parameter] = field(default_factory=list)
    responses: List[Response] = field(default_factory=list)
    auth_required: bool = True
    auth_methods: List[AuthMethod] = field(default_factory=lambda: [AuthMethod.BEARER])
    rate_limit: Optional[int] = None
    description: Optional[str] = None


@dataclass
class ApiDescriptor:
    """Complete API descriptor conforming to USS schema."""
    name: str
    version: str
    base_path: str
    endpoints: List[Endpoint] = field(default_factory=list)
    description: Optional[str] = None


@dataclass
class FieldMapping:
    """Mapping between source and target fields."""
    source_field: str
    target_field: str
    source_type: str
    target_type: str
    transformation: Optional[str] = None
    description: Optional[str] = None
    is_required: bool = False


@dataclass
class IntegrationMapping:
    """Complete mapping between source and target systems."""
    source_system: str
    target_system: str
    field_mappings: List[FieldMapping] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"
    created_at: str = None
    created_by: str = None

    def __post_init__(self):
        if self.created_at is None:
            from datetime import datetime
            self.created_at = datetime.utcnow().isoformat()


@dataclass
class AuthConfig:
    """Authentication configuration."""
    method: AuthMethod
    config: Dict[str, Any] = field(default_factory=dict)
    

@dataclass
class ServiceDescriptor:
    """Description of a remote service."""
    name: str
    base_url: str
    api_descriptor_url: Optional[str] = None
    auth_config: Optional[AuthConfig] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
