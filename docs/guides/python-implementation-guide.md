# Python Implementation Guide for UIP

**Version:** 1.0.0  
**Last Updated:** March 11, 2025

This guide will walk you through implementing the Universal Integration Protocol (UIP) in your Python applications. It covers installing the UCB library, basic usage, advanced features, and best practices.

## Table of Contents

1. [Installation](#1-installation)
2. [Basic Usage](#2-basic-usage)
3. [Creating Self-Describing APIs](#3-creating-self-describing-apis)
4. [Consuming External APIs](#4-consuming-external-apis)
5. [Resilience Patterns](#5-resilience-patterns)
6. [Custom Type Handling](#6-custom-type-handling)
7. [Integration with Web Frameworks](#7-integration-with-web-frameworks)
8. [Testing UIP Implementations](#8-testing-uip-implementations)
9. [Performance Optimization](#9-performance-optimization)
10. [Security Best Practices](#10-security-best-practices)

## 1. Installation

### Requirements

- Python 3.8 or higher
- pip (Python package installer)

### Install from PyPI

```bash
pip install universal-connector-block
```

### Install from Source

```bash
git clone https://github.com/uip-project/python-ucb.git
cd python-ucb
pip install -e .
```

### Verify Installation

```python
from universal_connector_block import UniversalConnectorBlock, __version__

print(f"UCB version: {__version__}")
```

## 2. Basic Usage

### Creating a UCB Instance

```python
from universal_connector_block import UniversalConnectorBlock

# Create a UCB instance for your application
ucb = UniversalConnectorBlock(
    app_name="MyPythonApp",
    version="1.0.0",
    base_path="/api/v1"
)
```

### Data Standardization and Translation

```python
# Convert native Python data to USS format
data = {
    "user_id": 123,
    "name": "John Doe",
    "email": "john@example.com",
    "is_active": True,
    "tags": ["customer", "premium"]
}

# Standardize to USS format
universal_data = ucb.standardize_output(data)
print(universal_data)
# Output:
# {
#   "data": {
#     "user_id": 123,
#     "name": "John Doe",
#     "email": "john@example.com",
#     "is_active": true,
#     "tags": ["customer", "premium"]
#   },
#   "metadata": {
#     "type": "Object",
#     "timestamp": "2025-03-11T12:34:56.789Z",
#     "source": "MyPythonApp/1.0.0",
#     "version": "1.0.0"
#   }
# }

# Translate back to native format
python_data = ucb.translate_input(universal_data)
print(python_data)
# Output: Original data dictionary
```

### Registering API Endpoints

```python
from universal_connector_block import HttpMethod, ParameterLocation

# Define handler functions
def get_user(user_id: str):
    # Your implementation to fetch a user
    return {"id": user_id, "name": "Example User"}

def create_user(name: str, email: str, role: str = "user"):
    # Your implementation to create a user
    return {"name": name, "email": email, "role": role, "id": "new-123"}

# Register endpoints
ucb.register_endpoint(
    path="/users/{user_id}",
    method=HttpMethod.GET,
    handler=get_user,
    description="Get a user by ID"
)

ucb.register_endpoint(
    path="/users",
    method=HttpMethod.POST,
    handler=create_user,
    description="Create a new user"
)
```

## 3. Creating Self-Describing APIs

### Generating API Descriptors

```python
# Generate a USS-compliant API descriptor
descriptor = ucb.generate_descriptor()
print(descriptor)

# Convert to JSON string for serving
descriptor_json = ucb.expose_descriptor()
```

### Exposing API Documentation with Flask

```python
from flask import Flask, jsonify
import json

app = Flask(__name__)

@app.route('/.well-known/uip-descriptor.json')
def get_descriptor():
    return jsonify(json.loads(ucb.expose_descriptor()))

# Optional: Generate OpenAPI/Swagger documentation
@app.route('/api/docs/swagger.json')
def get_swagger():
    from universal_connector_block.tools import convert_to_openapi
    openapi_spec = convert_to_openapi(ucb.generate_descriptor())
    return jsonify(openapi_spec)
```

### Using Detailed Type Annotations

```python
from typing import List, Dict, Optional, Union

# Define a data class for structure and type information
from dataclasses import dataclass

@dataclass
class User:
    id: str
    name: str
    email: str
    age: Optional[int] = None
    roles: List[str] = None
    metadata: Dict[str, any] = None

# Define handler with detailed type information
def update_user(
    user_id: str, 
    data: Dict[str, Union[str, int, List[str]]]
) -> User:
    # Implementation
    user = User(
        id=user_id,
        name=data.get("name", "Unknown"),
        email=data.get("email", "unknown@example.com"),
        age=data.get("age"),
        roles=data.get("roles", [])
    )
    return user

# The UCB will use type annotations to create better API descriptions
ucb.register_endpoint(
    path="/users/{user_id}",
    method=HttpMethod.PUT,
    handler=update_user,
    description="Update a user by ID"
)
```

## 4. Consuming External APIs

### Basic API Calls

```python
# Simple GET request
user_data = ucb.call_remote_api(
    url="https://api.example.com/users/123"
)

# POST request with data
new_user = ucb.call_remote_api(
    url="https://api.example.com/users",
    method="POST",
    data={
        "name": "Jane Smith",
        "email": "jane@example.com",
        "role": "admin"
    }
)
```

### Authentication

```python
# Bearer token authentication
user_data = ucb.call_remote_api(
    url="https://api.example.com/users/123",
    auth={
        "type": "bearer",
        "token": "your-oauth-token-here"
    }
)

# API key authentication
orders = ucb.call_remote_api(
    url="https://api.example.com/orders",
    auth={
        "type": "api_key",
        "key_name": "X-API-Key",
        "key_value": "your-api-key-here",
        "key_location": "header"
    }
)

# Basic authentication
report = ucb.call_remote_api(
    url="https://api.example.com/reports/monthly",
    auth={
        "type": "basic",
        "username": "user",
        "password": "pass"
    }
)
```

### Working with USS-Compatible Services

```python
import json
import requests

# Discover API capabilities
response = requests.get("https://api.example.com/.well-known/uip-descriptor.json")
api_descriptor = json.loads(response.text)

# Extract endpoints
endpoints = {}
for endpoint in api_descriptor.get("endpoints", []):
    key = f"{endpoint['method']} {endpoint['path']}"
    endpoints[key] = endpoint

# Find and use a specific endpoint
user_endpoint = endpoints.get("GET /users/{id}")
if user_endpoint:
    # Check parameters
    parameters = {p["name"]: p for p in user_endpoint.get("parameters", [])}
    
    # Make the call with proper parameters
    user = ucb.call_remote_api(
        url=f"https://api.example.com/users/123",
        method="GET"
    )
    print(user)
```

## 5. Resilience Patterns

### Retry Configuration

```python
# Configure retries for transient failures
result = ucb.call_remote_api(
    url="https://api.example.com/data",
    retry_attempts=3,  # Retry up to 3 times
    retry_backoff=2.0  # Exponential backoff multiplier
)
```

### Circuit Breaker Configuration

```python
# Configure the circuit breaker globally
ucb.circuit_breaker.failure_threshold = 5  # Open after 5 failures
ucb.circuit_breaker.reset_timeout = 30     # Reset after 30 seconds

# Make API call with circuit breaker protection
try:
    result = ucb.call_remote_api(
        url="https://api.example.com/data"
    )
except UcbError as e:
    if e.error_code == "CIRCUIT_OPEN":
        print("Circuit breaker is open due to multiple failures")
    else:
        print(f"API call failed: {e.message}")
```

### Timeout Handling

```python
# Set timeouts for API calls
try:
    result = ucb.call_remote_api(
        url="https://api.example.com/slow-operation",
        timeout=5  # 5 second timeout
    )
except UcbError as e:
    if e.error_code == "TIMEOUT_ERROR":
        print("The API call timed out")
    else:
        print(f"API call failed: {e.message}")
```

### Caching

```python
# Enable caching for read operations
cached_data = ucb.call_remote_api(
    url="https://api.example.com/frequently-accessed-data",
    use_cache=True,
    cache_ttl=300  # Cache for 5 minutes
)

# Clear the cache if needed
ucb.cacher.clear()
```

## 6. Custom Type Handling

### Creating Custom Type Mappers

```python
from universal_connector_block import TypeMapper
from decimal import Decimal
import datetime

class ExtendedTypeMapper(TypeMapper):
    def __init__(self):
        super().__init__()
        # Add custom type mappings
        self.PYTHON_TO_USS.update({
            Decimal: "Decimal",
            datetime.date: "Date",
            datetime.datetime: "DateTime",
            bytes: "Binary",
            set: "Array"
        })
        
        self.USS_TO_PYTHON.update({
            "Decimal": Decimal,
            "Date": datetime.date,
            "DateTime": datetime.datetime,
            "Binary": bytes
        })
    
    def python_to_uss(self, py_type) -> str:
        # Handle custom types
        if hasattr(py_type, "__origin__") and py_type.__origin__ is set:
            return "Array"
        return super().python_to_uss(py_type)
    
    def validate_and_convert(self, value, uss_type: str):
        # Handle custom validation and conversion
        if uss_type == "Decimal":
            if isinstance(value, (int, float, str)):
                return Decimal(str(value))
            raise ValidationError(f"Cannot convert {value} to Decimal")
            
        # Handle special date/time formats
        if uss_type == "Date" and isinstance(value, str):
            try:
                return datetime.date.fromisoformat(value)
            except ValueError:
                raise ValidationError(f"Cannot convert {value} to Date")
                
        return super().validate_and_convert(value, uss_type)

# Use the custom type mapper
ucb.type_mapper = ExtendedTypeMapper()
```

### Working with Custom Objects

```python
# Define a custom class
class Product:
    def __init__(self, id, name, price, inventory):
        self.id = id
        self.name = name
        self.price = price
        self.inventory = inventory
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "inventory": self.inventory
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            price=data.get("price"),
            inventory=data.get("inventory")
        )

# Create a custom serializer/deserializer
from universal_connector_block import register_type_adapter

# Register adapter functions
register_type_adapter(
    Product,
    serialize_fn=lambda obj: obj.to_dict(),
    deserialize_fn=lambda data: Product.from_dict(data)
)

# Now you can use Product objects directly
product = Product("prod-123", "Example Product", 29.99, 100)
uss_data = ucb.standardize_output(product)

# And convert back
product_copy = ucb.translate_input(uss_data, "Product")
```

## 7. Integration with Web Frameworks

### Flask Integration

```python
from flask import Flask, request, jsonify
from universal_connector_block import UniversalConnectorBlock, HttpMethod

app = Flask(__name__)
ucb = UniversalConnectorBlock("FlaskApp", "1.0.0", "/api")

# Define handler functions with Flask request integration
def get_users():
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)
    # Implementation...
    return {"users": [...], "total": 100, "page": page, "limit": limit}

def create_user():
    data = request.json
    # Implementation...
    return {"id": "new-123", "name": data.get("name"), "created": True}

# Register endpoints
ucb.register_endpoint("/users", HttpMethod.GET, get_users)
ucb.register_endpoint("/users", HttpMethod.POST, create_user)

# Flask route that uses UCB for processing
@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def api_handler(path):
    try:
        # Extract request data
        path = f"/{path}"
        method = request.method
        params = {}
        
        # Include query parameters
        params.update(request.args.to_dict())
        
        # Include body for POST/PUT
        if request.json and request.method in ['POST', 'PUT', 'PATCH']:
            params['__body'] = request.json
            
        # Handle the request through UCB
        result = ucb.handle_request(
            path=path,
            method=method,
            params=params,
            headers=dict(request.headers)
        )
        
        return jsonify(result['data']), 200
    except Exception as e:
        if hasattr(e, 'to_dict') and callable(getattr(e, 'to_dict')):
            return jsonify(e.to_dict()), getattr(e, 'status_code', 500)
        return jsonify({"error": str(e)}), 500
```

### FastAPI Integration

```python
from fastapi import FastAPI, Depends, HTTPException
from universal_connector_block import UniversalConnectorBlock

app = FastAPI()
ucb = UniversalConnectorBlock("FastAPIApp", "1.0.0", "/api")

# Expose API descriptor
@app.get("/.well-known/uip-descriptor.json")
async def get_descriptor():
    return ucb.generate_descriptor()

# Define models with Pydantic
from pydantic import BaseModel, Field, EmailStr

class UserCreate(BaseModel):
    name: str = Field(..., title="User name", min_length=2)
    email: EmailStr = Field(..., title="Email address")
    role: str = Field("user", title="User role")

class User(UserCreate):
    id: str = Field(..., title="User ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)

# FastAPI endpoints that leverage UCB
@app.post("/api/users", response_model=User)
async def create_user(user: UserCreate):
    try:
        # Use UCB to handle data validation and transformation
        result = ucb.handle_request(
            path="/users",
            method="POST",
            params={"__body": user.dict()},
            headers={}
        )
        
        if result["status"] == "success":
            return result["data"]
        else:
            raise HTTPException(status_code=400, detail="Failed to create user")
    except Exception as e:
        if hasattr(e, 'status_code'):
            raise HTTPException(status_code=e.status_code, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# FastAPI dependency for UCB-based API calls
def api_client():
    client = ucb
    yield client

@app.get("/external-data")
async def get_external_data(ucb_client: UniversalConnectorBlock = Depends(api_client)):
    try:
        data = ucb_client.call_remote_api(
            url="https://api.example.com/data",
            use_cache=True
        )
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Django Integration

```python
# views.py
from django.http import JsonResponse
from django.views import View
import json
from universal_connector_block import UniversalConnectorBlock, HttpMethod, UcbError

# Create UCB instance
ucb = UniversalConnectorBlock("DjangoApp", "1.0.0", "/api")

# Define handler functions
def get_products(category=None, limit=10, offset=0):
    # Your implementation
    return {"products": [...], "total": 100}

def create_product(name, price, description=None, category=None):
    # Your implementation
    return {"id": "new-123", "name": name, "price": price, "created": True}

# Register endpoints
ucb.register_endpoint("/products", HttpMethod.GET, get_products)
ucb.register_endpoint("/products", HttpMethod.POST, create_product)

# Django view that uses UCB
class UcbView(View):
    def dispatch(self, request, *args, **kwargs):
        try:
            # Extract path from URL
            path = request.path.replace("/api", "", 1) or "/"
            method = request.method
            params = {}
            
            # Process query parameters
            params.update(request.GET.dict())
            
            # Process body for POST/PUT
            if request.method in ["POST", "PUT", "PATCH"]:
                try:
                    params["__body"] = json.loads(request.body)
                except json.JSONDecodeError:
                    return JsonResponse(
                        {"error": "Invalid JSON in request body"}, 
                        status=400
                    )
            
            # Handle the request through UCB
            result = ucb.handle_request(
                path=path,
                method=method,
                params=params,
                headers=dict(request.headers)
            )
            
            return JsonResponse(result["data"])
            
        except UcbError as e:
            return JsonResponse(e.to_dict(), status=e.status_code)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

# urls.py
from django.urls import path, re_path
from . import views

urlpatterns = [
    path('.well-known/uip-descriptor.json', 
         lambda request: JsonResponse(json.loads(ucb.expose_descriptor()))),
    re_path(r'^api/.*, views.UcbView.as_view()),
]
```

## 8. Testing UIP Implementations

### Unit Testing with pytest

```python
import pytest
from universal_connector_block import UniversalConnectorBlock, ValidationError

@pytest.fixture
def ucb():
    return UniversalConnectorBlock("TestApp", "1.0.0", "/api")

def test_standardize_output(ucb):
    """Test data standardization."""
    data = {"name": "Test", "value": 123}
    universal_data = ucb.standardize_output(data)
    parsed = json.loads(universal_data)
    
    assert "data" in parsed
    assert "metadata" in parsed
    assert parsed["data"] == data
    assert parsed["metadata"]["type"] == "Object"
    
def test_translate_input(ucb):
    """Test data translation."""
    original_data = {"name": "Test", "value": 123}
    universal_data = json.dumps({
        "data": original_data,
        "metadata": {"type": "Object"}
    })
    
    result = ucb.translate_input(universal_data)
    assert result == original_data
    
def test_type_validation(ucb):
    """Test type validation and conversion."""
    # Valid conversion
    universal_data = json.dumps({
        "data": "42",
        "metadata": {"type": "String"}
    })
    result = ucb.translate_input(universal_data, "Integer")
    assert result == 42
    
    # Invalid conversion
    universal_data = json.dumps({
        "data": "not-a-number",
        "metadata": {"type": "String"}
    })
    with pytest.raises(ValidationError):
        ucb.translate_input(universal_data, "Integer")
```

### Integration Testing with Mock Server

```python
import pytest
import responses
from universal_connector_block import UniversalConnectorBlock, UcbError

@pytest.fixture
def ucb():
    return UniversalConnectorBlock("TestApp", "1.0.0", "/api")

@responses.activate
def test_api_call_success(ucb):
    """Test successful API call."""
    # Mock response
    responses.add(
        responses.GET,
        "https://api.example.com/users/123",
        json={"id": "123", "name": "Test User"},
        status=200
    )
    
    # Make the API call
    result = ucb.call_remote_api(
        url="https://api.example.com/users/123"
    )
    
    # Verify result
    assert result["id"] == "123"
    assert result["name"] == "Test User"
    
@responses.activate
def test_api_call_error(ucb):
    """Test API call with error response."""
    # Mock error response
    responses.add(
        responses.GET,
        "https://api.example.com/users/999",
        json={"message": "User not found"},
        status=404
    )
    
    # Make the API call that should fail
    with pytest.raises(UcbError) as excinfo:
        ucb.call_remote_api(
            url="https://api.example.com/users/999"
        )
    
    # Verify error
    assert excinfo.value.error_code == "REMOTE_CLIENT_ERROR_404"
    assert excinfo.value.status_code == 404
    
@responses.activate
def test_retry_behavior(ucb):
    """Test retry behavior on server errors."""
    # Add multiple responses to simulate retry
    responses.add(
        responses.GET,
        "https://api.example.com/flaky",
        json={"message": "Server Error"},
        status=500
    )
    
    responses.add(
        responses.GET,
        "https://api.example.com/flaky",
        json={"message": "Server Error"},
        status=500
    )
    
    responses.add(
        responses.GET,
        "https://api.example.com/flaky",
        json={"status": "success"},
        status=200
    )
    
    # Make the API call with retry
    result = ucb.call_remote_api(
        url="https://api.example.com/flaky",
        retry_attempts=3
    )
    
    # Verify success after retries
    assert result["status"] == "success"
    assert len(responses.calls) == 3  # Verify it made 3 calls
```

### Performance Testing

```python
import time
import statistics
import pytest

@pytest.fixture
def ucb():
    return UniversalConnectorBlock("TestApp", "1.0.0", "/api")

def test_standardization_performance(ucb):
    """Test performance of data standardization."""
    # Create a complex data structure
    data = {
        "id": "test-123",
        "name": "Performance Test",
        "values": [i for i in range(1000)],
        "nested": {
            "key1": "value1",
            "key2": "value2",
            # More nested data...
        }
    }
    
    # Measure time for multiple calls
    times = []
    iterations = 1000
    
    for _ in range(iterations):
        start = time.time()
        ucb.standardize_output(data)
        end = time.time()
        times.append((end - start) * 1000)  # Convert to ms
    
    # Calculate statistics
    avg_time = statistics.mean(times)
    max_time = max(times)
    p95_time = sorted(times)[int(iterations * 0.95)]
    
    print(f"Standardization performance:")
    print(f"  Average: {avg_time:.2f}ms")
    print(f"  P95: {p95_time:.2f}ms")
    print(f"  Max: {max_time:.2f}ms")
    
    # Assert performance requirements
    assert avg_time < 5.0, f"Average time too high: {avg_time:.2f}ms"
    assert p95_time < 10.0, f"P95 time too high: {p95_time:.2f}ms"
```

## 9. Performance Optimization

### Caching Type Information

```python
from universal_connector_block import TypeMapper
import functools

class CachedTypeMapper(TypeMapper):
    def __init__(self):
        super().__init__()
        self._type_cache = {}
        
    @functools.lru_cache(maxsize=1000)
    def python_to_uss(self, py_type) -> str:
        # This method is now cached with LRU cache
        return super().python_to_uss(py_type)
    
    @functools.lru_cache(maxsize=1000)
    def infer_type_from_value(self, value) -> str:
        # Cache type inference results
        return super().infer_type_from_value(value)

# Use the cached type mapper
ucb.type_mapper = CachedTypeMapper()
```

### Batch Processing for Large Datasets

```python
def process_large_dataset(data_list, batch_size=100):
    """Process a large dataset in batches to reduce memory usage."""
    results = []
    
    # Process in batches
    for i in range(0, len(data_list), batch_size):
        batch = data_list[i:i+batch_size]
        
        # Process the batch
        batch_results = []
        for item in batch:
            # Standardize each item
            uss_item = ucb.standardize_output(item)
            
            # Process the standardized item (e.g., send to remote API)
            # ...
            
            # Add to batch results
            batch_results.append(result)
        
        # Add batch results to overall results
        results.extend(batch_results)
    
    return results
```

### Streaming Response Processing

```python
import json
from typing import Iterator, Dict, Any

def stream_process_large_response(response_text: str) -> Iterator[Dict[str, Any]]:
    """Stream-process a large JSON array response to reduce memory usage."""
    # Check if it starts with an array
    response_text = response_text.strip()
    if not response_text.startswith('['):
        # Not an array, just parse normally
        yield json.loads(response_text)
        return
    
    # Stream process the array
    decoder = json.JSONDecoder()
    idx = 0
    
    # Skip the opening bracket
    idx += 1
    
    # Process each item in the array
    while idx < len(response_text):
        try:
            # Skip whitespace
            while idx < len(response_text) and response_text[idx].isspace():
                idx += 1
                
            if idx >= len(response_text) or response_text[idx] == ']':
                break
                
            # Decode the next item
            obj, idx = decoder.raw_decode(response_text, idx=idx)
            
            # Process the item
            yield obj
            
            # Skip comma
            while idx < len(response_text) and response_text[idx].isspace():
                idx += 1
                
            if idx < len(response_text) and response_text[idx] == ',':
                idx += 1
                
        except json.JSONDecodeError:
            break

# Example usage
async def process_large_response(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            text = await response.text()
            
            for item in stream_process_large_response(text):
                # Process each item individually
                process_item(item)
```

## 10. Security Best Practices

### Secure Authentication Handling

```python
import os
from cryptography.fernet import Fernet
from universal_connector_block import UniversalConnectorBlock

# Create a secure token storage
class SecureTokenStorage:
    def __init__(self, encryption_key=None):
        # Generate or use provided encryption key
        self.key = encryption_key or os.environ.get('ENCRYPTION_KEY') or Fernet.generate_key()
        self.cipher = Fernet(self.key)
        self.tokens = {}
        
    def store_token(self, service_id, token):
        """Securely store a token."""
        encrypted = self.cipher.encrypt(token.encode())
        self.tokens[service_id] = encrypted
        
    def get_token(self, service_id):
        """Retrieve and decrypt a token."""
        if service_id not in self.tokens:
            return None
            
        encrypted = self.tokens[service_id]
        return self.cipher.decrypt(encrypted).decode()

# Use the secure token storage
token_storage = SecureTokenStorage()
token_storage.store_token("payment-api", "very-secret-token")

# Make authenticated API calls
def call_secure_api(endpoint, data=None):
    token = token_storage.get_token("payment-api")
    if not token:
        raise ValueError("Missing authentication token")
        
    return ucb.call_remote_api(
        url=f"https://api.payment-service.com/{endpoint}",
        method="POST" if data else "GET",
        data=data,
        auth={
            "type": "bearer",
            "token": token
        }
    )
```

### Input Validation and Sanitization

```python
from universal_connector_block import ValidationError
import re

def validate_user_input(user_input, input_type):
    """Validate user input before processing."""
    if input_type == "email":
        # Simple email validation
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", user_input):
            raise ValidationError("Invalid email format", [{"field": "email", "value": user_input}])
            
    elif input_type == "username":
        # Username validation
        if not re.match(r"^[a-zA-Z0-9_]{3,20}$", user_input):
            raise ValidationError(
                "Username must be 3-20 characters and contain only letters, numbers, and underscores",
                [{"field": "username", "value": user_input}]
            )
            
    elif input_type == "url":
        # URL validation
        if not user_input.startswith(("http://", "https://")):
            raise ValidationError(
                "URL must begin with http:// or https://",
                [{"field": "url", "value": user_input}]
            )
    
    return user_input

# Use in API handlers
def create_user_handler(username, email, website=None):
    # Validate inputs
    username = validate_user_input(username, "username")
    email = validate_user_input(email, "email")
    
    if website:
        website = validate_user_input(website, "url")
        
    # Process validated inputs
    # ...
    
    return {"username": username, "email": email, "website": website}

# Register with UCB
ucb.register_endpoint(
    path="/users",
    method="POST",
    handler=create_user_handler
)
```

### Secure Error Handling

```python
from universal_connector_block import UcbError

def secure_error_handler(func):
    """Decorator to ensure secure error handling."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except UcbError:
            # Pass through UCB errors which are already properly formatted
            raise
        except ValueError as e:
            # Convert to proper error response without sensitive details
            raise UcbError(
                "VALIDATION_ERROR",
                str(e),
                status_code=400
            )
        except Exception as e:
            # Log the full error internally
            logger.exception(f"Internal error: {str(e)}")
            
            # Return a sanitized error to the client
            raise UcbError(
                "INTERNAL_ERROR",
                "An internal error occurred",
                status_code=500
            )
    return wrapper

# Apply to handlers
@secure_error_handler
def process_payment(user_id, amount, payment_method):
    # Implementation with proper error handling
    # ...
    
    return {"status": "success", "transaction_id": "tx123"}

# Register with UCB
ucb.register_endpoint(
    path="/payments",
    method="POST",
    handler=process_payment
)
```

## Conclusion

This guide has covered the implementation of the Universal Integration Protocol (UIP) in Python applications. By following these patterns and best practices, you can create robust, secure, and efficient integrations between your applications and other systems.

For more information, refer to:

- [UIP Protocol Specification](../specifications/protocol-spec.md)
- [Python UCB API Reference](../api/python-ucb-api.md)
- [UCB Testing Framework](../../tests/conformance/README.md)

If you have questions or need assistance, please [open an issue](https://github.com/uip-project/python-ucb/issues) in the repository.

---

**Last Updated:** March 11, 2025