"""
Core implementation of the Universal Connector Block for Python.
"""

import json
import inspect
import datetime
import logging
import uuid
from typing import Any, Dict, List, Optional, Union, Callable, Type, TypeVar, get_type_hints

from .enums import HttpMethod, AuthMethod, ParameterLocation
from .errors import UcbError, ValidationError
from .types import TypeMapper
from .resilience import CircuitBreaker, RateLimiter, Cacher
from .models import Endpoint, Parameter, Response, ApiDescriptor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ucb")

# Type definitions
T = TypeVar('T')


class JsonEncoder(json.JSONEncoder):
    """Extended JSON encoder that handles additional Python types."""
    
    def default(self, obj):
        if hasattr(obj, "__dataclass_fields__"):
            # Handle dataclasses
            return {f: getattr(obj, f) for f in obj.__dataclass_fields__}
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, bytes):
            import base64
            return base64.b64encode(obj).decode('ascii')
        if inspect.isfunction(obj) or inspect.ismethod(obj):
            return obj.__name__
        if isinstance(obj, type):
            return obj.__name__
        return super().default(obj)


class UniversalConnectorBlock:
    """Main UCB implementation that provides USS compatibility."""
    
    def __init__(self, app_name: str, version: str, base_path: str = "/api"):
        """
        Initialize a new Universal Connector Block instance.
        
        Args:
            app_name: Name of the application using the UCB
            version: Version of the application
            base_path: Base path for API endpoints
        """
        self.app_name = app_name
        self.version = version
        self.base_path = base_path
        self.endpoints: List[Endpoint] = []
        self.circuit_breaker = CircuitBreaker()
        self.rate_limiter = RateLimiter()
        self.cacher = Cacher()
        self.type_mapper = TypeMapper()
        
    def generate_descriptor(self) -> Dict[str, Any]:
        """Generate a USS-compliant API descriptor."""
        descriptor = ApiDescriptor(
            name=self.app_name,
            version=self.version,
            base_path=self.base_path,
            endpoints=self.endpoints
        )
        
        # Convert to USS format
        return {
            "@context": "https://uip.org/context/v1",
            "@type": "APIDescriptor",
            "@id": f"https://api.example.com/{self.app_name}",
            "version": self.version,
            "name": self.app_name,
            "basePath": self.base_path,
            "endpoints": [self._endpoint_to_uss(endpoint) for endpoint in self.endpoints]
        }
    
    def _endpoint_to_uss(self, endpoint: Endpoint) -> Dict[str, Any]:
        """Convert an Endpoint to USS format."""
        return {
            "path": endpoint.path,
            "method": endpoint.method.value if isinstance(endpoint.method, HttpMethod) else endpoint.method,
            "parameters": [
                {
                    "name": param.name,
                    "location": param.location.value if isinstance(param.location, ParameterLocation) else param.location,
                    "required": param.required,
                    "type": param.type,
                    "description": param.description
                }
                for param in endpoint.parameters
            ],
            "responses": [
                {
                    "statusCode": resp.status_code,
                    "contentType": resp.content_type,
                    "schema": resp.schema,
                    "description": resp.description
                }
                for resp in endpoint.responses
            ],
            "authentication": {
                "required": endpoint.auth_required,
                "methods": [method.value if isinstance(method, AuthMethod) else method 
                           for method in endpoint.auth_methods] if endpoint.auth_methods else []
            },
            "rateLimit": endpoint.rate_limit,
            "description": endpoint.description
        }
        
    def register_endpoint(self, 
                         path: str, 
                         method: Union[str, HttpMethod], 
                         handler: Callable,
                         auth_required: bool = True,
                         auth_methods: List[Union[str, AuthMethod]] = None,
                         rate_limit: Optional[int] = None,
                         description: Optional[str] = None) -> None:
        """
        Register an API endpoint with the UCB.
        
        Args:
            path: URL path for the endpoint, can include path parameters in {param} format
            method: HTTP method (GET, POST, etc.)
            handler: Function that will handle requests to this endpoint
            auth_required: Whether authentication is required
            auth_methods: Supported authentication methods
            rate_limit: Rate limit for this endpoint (requests per minute)
            description: Human-readable description of the endpoint
        """
        if isinstance(method, str):
            method = HttpMethod(method.upper())
            
        if auth_methods:
            auth_methods = [AuthMethod(am) if isinstance(am, str) else am 
                           for am in auth_methods]
        else:
            auth_methods = [AuthMethod.BEARER]
        
        # Extract parameters from function signature
        sig = inspect.signature(handler)
        type_hints = get_type_hints(handler)
        
        parameters = []
        for name, param in sig.parameters.items():
            if name == 'self':
                continue
                
            param_type = type_hints.get(name, Any)
            uss_type = self.type_mapper.python_to_uss(param_type)
            
            # Determine parameter location (simple heuristic)
            if name == 'body' or param.annotation == dict:
                location = ParameterLocation.BODY
            elif path and f"{{{name}}}" in path:
                location = ParameterLocation.PATH
            else:
                location = ParameterLocation.QUERY
                
            # Determine if parameter is required
            required = param.default == inspect.Parameter.empty
            default_value = None if required else param.default
            
            parameters.append(Parameter(
                name=name,
                type=uss_type,
                location=location,
                required=required,
                default_value=default_value
            ))
            
        # Extract response information
        return_type = type_hints.get('return')
        responses = []
        
        if return_type:
            uss_type = self.type_mapper.python_to_uss(return_type)
            responses.append(Response(
                status_code=200,
                content_type="application/json",
                schema={"type": uss_type}
            ))
        
        # Add default error responses
        responses.append(Response(
            status_code=400,
            content_type="application/json",
            schema={"type": "Error"},
            description="Bad Request"
        ))
        
        responses.append(Response(
            status_code=500,
            content_type="application/json",
            schema={"type": "Error"},
            description="Internal Server Error"
        ))
        
        # Create and register the endpoint
        endpoint = Endpoint(
            path=path,
            method=method,
            handler=handler,
            parameters=parameters,
            responses=responses,
            auth_required=auth_required,
            auth_methods=auth_methods,
            rate_limit=rate_limit,
            description=description
        )
        
        self.endpoints.append(endpoint)
        
    def standardize_output(self, native_data: Any) -> str:
        """
        Convert native Python data to USS format.
        
        Args:
            native_data: The Python data to convert
            
        Returns:
            USS-formatted JSON string representation
        """
        # Determine the USS type
        uss_type = self.type_mapper.infer_type_from_value(native_data)
        
        # Create the standardized output
        result = {
            "data": native_data,
            "metadata": {
                "type": uss_type,
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "source": f"{self.app_name}/{self.version}",
                "version": "1.0.0"
            }
        }
        
        # Convert to JSON
        return json.dumps(result, cls=JsonEncoder)
        
    def translate_input(self, universal_data: str, expected_type: Optional[str] = None) -> Any:
        """
        Convert USS format back to native Python data.
        
        Args:
            universal_data: USS-formatted JSON string
            expected_type: Expected USS type for validation
            
        Returns:
            Native Python data
            
        Raises:
            ValidationError: If the data doesn't match the expected type
        """
        try:
            parsed = json.loads(universal_data)
        except json.JSONDecodeError as e:
            raise ValidationError("Invalid JSON data", 
                                 [{"error": str(e)}])
        
        # Validate structure                         
        if not isinstance(parsed, dict) or "data" not in parsed:
            raise ValidationError("Invalid USS format: missing 'data' field", 
                                 [{"received": list(parsed.keys()) if isinstance(parsed, dict) else type(parsed).__name__}])
        
        data = parsed["data"]
        
        # If expected_type is provided, validate and convert
        if expected_type:
            return self.type_mapper.validate_and_convert(data, expected_type)
            
        return data
        
    def call_remote_api(self, 
                        url: str, 
                        method: str = "GET", 
                        data: Optional[Dict[str, Any]] = None,
                        headers: Optional[Dict[str, str]] = None,
                        auth: Optional[Dict[str, str]] = None,
                        use_cache: bool = False,
                        retry_attempts: int = 3,
                        timeout: int = 30) -> Dict[str, Any]:
        """
        Call a remote API with resilience patterns and error handling.
        
        Args:
            url: The URL to call
            method: HTTP method (GET, POST, etc.)
            data: Data to send in the request body
            headers: HTTP headers to include
            auth: Authentication configuration
            use_cache: Whether to use caching
            retry_attempts: Number of retry attempts for transient errors
            timeout: Request timeout in seconds
            
        Returns:
            Response data from the API
            
        Raises:
            UcbError: For API call failures
        """
        import time  # Import here to avoid circular imports
        import requests
        
        # Check circuit breaker
        if not self.circuit_breaker.allow_request():
            raise UcbError("CIRCUIT_OPEN", 
                          "Circuit breaker is open due to repeated failures",
                          status_code=503)
                          
        # Check rate limiter
        if not self.rate_limiter.allow_request():
            raise UcbError("RATE_LIMIT_EXCEEDED",
                          "Rate limit exceeded for API calls",
                          status_code=429)
                          
        # Check cache if enabled
        if use_cache and method.upper() == "GET":
            cache_key = self.cacher.generate_key(url, method, data, headers, auth)
            cached_response = self.cacher.get(cache_key)
            if cached_response:
                logger.debug(f"Cache hit for {url}")
                return cached_response
        
        # Prepare headers
        if headers is None:
            headers = {}
            
        # Add default headers if not present
        if "Accept" not in headers:
            headers["Accept"] = "application/json"
        if "Content-Type" not in headers and data:
            headers["Content-Type"] = "application/json"
            
        # Prepare authentication
        session = requests.Session()
        if auth:
            auth_type = auth.get("type", "bearer")
            
            if auth_type == "bearer":
                headers["Authorization"] = f"Bearer {auth.get('token', '')}"
            elif auth_type == "basic":
                username = auth.get("username", "")
                password = auth.get("password", "")
                session.auth = (username, password)
            elif auth_type == "api_key":
                key_name = auth.get("key_name", "api_key")
                key_value = auth.get("key_value", "")
                key_location = auth.get("key_location", "header")
                
                if key_location == "header":
                    headers[key_name] = key_value
                elif key_location == "query":
                    if "?" not in url:
                        url = f"{url}?{key_name}={key_value}"
                    else:
                        url = f"{url}&{key_name}={key_value}"
        
        # Execute request with retry logic
        attempt = 0
        last_error = None
        
        while attempt < retry_attempts:
            try:
                attempt += 1
                
                # Make the request
                response = session.request(
                    method=method.upper(),
                    url=url,
                    json=data if data and headers.get("Content-Type") == "application/json" else None,
                    data=data if data and headers.get("Content-Type") != "application/json" else None,
                    headers=headers,
                    timeout=timeout
                )
                
                # Check for HTTP errors
                if response.status_code >= 400:
                    error_msg = f"API request failed with status {response.status_code}"
                    error_details = []
                    
                    try:
                        error_data = response.json()
                        if isinstance(error_data, dict):
                            error_msg = error_data.get("message", error_msg)
                            error_details = error_data.get("details", [])
                    except:
                        pass
                        
                    if response.status_code >= 500:
                        # Server error, may retry
                        last_error = UcbError(
                            f"REMOTE_SERVER_ERROR_{response.status_code}",
                            error_msg,
                            error_details,
                            status_code=response.status_code
                        )
                        logger.warning(f"Server error on attempt {attempt}: {error_msg}")
                        
                        if attempt < retry_attempts:
                            # Exponential backoff
                            backoff_time = 0.5 * (2 ** (attempt - 1))
                            logger.info(f"Retrying in {backoff_time:.2f} seconds...")
                            time.sleep(backoff_time)
                            continue
                    else:
                        # Client error, don't retry
                        self.circuit_breaker.record_success()  # Don't penalize for 4xx errors
                        raise UcbError(
                            f"REMOTE_CLIENT_ERROR_{response.status_code}",
                            error_msg,
                            error_details,
                            status_code=response.status_code
                        )
                
                # Process successful response
                try:
                    result = response.json() if response.text else {}
                except json.JSONDecodeError:
                    result = {"raw_content": response.text}
                    
                # Record success
                self.circuit_breaker.record_success()
                
                # Cache the result if enabled
                if use_cache and method.upper() == "GET":
                    cache_key = self.cacher.generate_key(url, method, data, headers, auth)
                    self.cacher.set(cache_key, result)
                    
                return result
                
            except requests.RequestException as e:
                logger.warning(f"Request failed on attempt {attempt}: {str(e)}")
                last_error = UcbError(
                    "CONNECTION_ERROR",
                    f"Connection error: {str(e)}",
                    status_code=503
                )
                
                if attempt < retry_attempts:
                    # Exponential backoff
                    backoff_time = 0.5 * (2 ** (attempt - 1))
                    logger.info(f"Retrying in {backoff_time:.2f} seconds...")
                    time.sleep(backoff_time)
                else:
                    # Record failure after all retries
                    self.circuit_breaker.record_failure()
                    
        # If we got here, all retries failed
        if last_error:
            raise last_error
        else:
            raise UcbError(
                "MAX_RETRIES_EXCEEDED",
                f"Request failed after {retry_attempts} attempts",
                status_code=503
            )
            
    def expose_descriptor(self) -> str:
        """
        Returns the USS API descriptor as a JSON string.
        
        Returns:
            JSON string representation of the API descriptor
        """
        descriptor = self.generate_descriptor()
        return json.dumps(descriptor, cls=JsonEncoder)
        
    def handle_request(self, 
                      path: str, 
                      method: str, 
                      params: Dict[str, Any] = None, 
                      headers: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Process an incoming request according to registered endpoints.
        
        Args:
            path: Request path
            method: HTTP method
            params: Request parameters (query params and body)
            headers: HTTP headers
            
        Returns:
            Response data
            
        Raises:
            UcbError: If the endpoint is not found or request processing fails
        """
        if params is None:
            params = {}
        if headers is None:
            headers = {}
            
        # Find matching endpoint
        endpoint = None
        path_params = {}
        
        for ep in self.endpoints:
            # Check if method matches
            if ep.method.value != method.upper():
                continue
                
            # Check if path matches (with path parameters)
            ep_path_parts = ep.path.split('/')
            req_path_parts = path.split('/')
            
            if len(ep_path_parts) != len(req_path_parts):
                continue
                
            match = True
            extracted_params = {}
            
            for i, (ep_part, req_part) in enumerate(zip(ep_path_parts, req_path_parts)):
                if ep_part.startswith('{') and ep_part.endswith('}'):
                    # This is a path parameter
                    param_name = ep_part[1:-1]
                    extracted_params[param_name] = req_part
                elif ep_part != req_part:
                    match = False
                    break
                    
            if match:
                endpoint = ep
                path_params = extracted_params
                break
                
        if not endpoint:
            raise UcbError(
                "ENDPOINT_NOT_FOUND",
                f"No endpoint found for {method} {path}",
                status_code=404
            )
            
        # Authentication check
        if endpoint.auth_required:
            auth_header = headers.get('Authorization', '')
            if not auth_header:
                raise UcbError(
                    "AUTHENTICATION_REQUIRED",
                    "Authentication is required for this endpoint",
                    status_code=401
                )
                
            # Here you would implement your authentication logic
            # For simplicity, we just check if Authorization header exists
            
        # Extract and validate parameters
        handler_params = {}
        
        for param in endpoint.parameters:
            param_name = param.name
            param_location = param.location
            param_type = param.type
            
            if param_location == ParameterLocation.PATH:
                if param_name in path_params:
                    value = path_params[param_name]
                    try:
                        handler_params[param_name] = self.type_mapper.validate_and_convert(value, param_type)
                    except ValidationError as e:
                        raise ValidationError(
                            f"Invalid path parameter: {param_name}",
                            e.details
                        )
                elif param.required:
                    raise ValidationError(
                        f"Missing required path parameter: {param_name}",
                        [{"parameter": param_name, "location": "path"}]
                    )
                    
            elif param_location == ParameterLocation.QUERY:
                if param_name in params:
                    value = params[param_name]
                    try:
                        handler_params[param_name] = self.type_mapper.validate_and_convert(value, param_type)
                    except ValidationError as e:
                        raise ValidationError(
                            f"Invalid query parameter: {param_name}",
                            e.details
                        )
                elif param.required:
                    raise ValidationError(
                        f"Missing required query parameter: {param_name}",
                        [{"parameter": param_name, "location": "query"}]
                    )
                    
            elif param_location == ParameterLocation.BODY:
                # Assume body is passed as special '__body' parameter in params
                if '__body' in params:
                    body = params['__body']
                    if param_type == "Object" and param_name != '__body':
                        # Extract just one field from body
                        if isinstance(body, dict) and param_name in body:
                            handler_params[param_name] = body[param_name]
                        elif param.required:
                            raise ValidationError(
                                f"Missing required body parameter: {param_name}",
                                [{"parameter": param_name, "location": "body"}]
                            )
                    else:
                        # Use entire body
                        handler_params[param_name] = body
                elif param.required:
                    raise ValidationError(
                        f"Missing required body parameter: {param_name}",
                        [{"parameter": param_name, "location": "body"}]
                    )
                    
        # Call the handler
        try:
            result = endpoint.handler(**handler_params)
            return {
                "status": "success",
                "data": result
            }
        except Exception as e:
            if isinstance(e, UcbError):
                raise e
            else:
                logger.exception(f"Error handling request: {str(e)}")
                raise UcbError(
                    "INTERNAL_ERROR",
                    f"Internal server error: {str(e)}",
                    status_code=500
                )