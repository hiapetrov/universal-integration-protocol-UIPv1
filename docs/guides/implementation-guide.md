# Universal Integration Protocol (UIP)
# Developer Implementation Guide

**Version:** 1.0.0  
**Date:** March 9, 2025

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Installing the Universal Connector Block](#installing-the-ucb)
4. [Basic Usage](#basic-usage)
5. [Creating Self-Describing APIs](#self-describing-apis)
6. [Consuming External APIs](#consuming-external-apis)
7. [Advanced Features](#advanced-features)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)
10. [Appendix: Language-Specific Considerations](#appendix-language-specific)

## 1. Introduction <a name="introduction"></a>

The Universal Integration Protocol (UIP) is designed to make software integration seamless across different languages, frameworks, and platforms. This guide will help you implement UIP in your applications, whether you're exposing APIs or consuming them.

### Key Benefits

- **Language-Agnostic Integration:** Connect any application regardless of the programming language used
- **Automatic API Discovery:** Self-describing APIs make integration points discoverable
- **Resilient Connections:** Built-in circuit breakers, retries, and error handling
- **AI-Powered Integration:** Leverage AI to generate integration code and mappings

### Protocol Components

UIP consists of three main components:

1. **Universal Semantic Schema (USS):** A standardized format for describing data and APIs
2. **Universal Connector Block (UCB):** A library available in multiple languages that implements the protocol
3. **AI Integration Middleware (AIM):** AI-powered tools to analyze, map, and generate integration code

## 2. Getting Started <a name="getting-started"></a>

Before diving into implementation, it's helpful to understand the core concepts of UIP:

- **USS Schema:** JSON-LD based schemas that describe your API's capabilities and data types
- **UCB Library:** The implementation of UIP that you'll add to your application
- **Standardization:** The process of converting between native data formats and USS
- **Self-Description:** How your API exposes its capabilities to other systems

To implement UIP, you'll need to:

1. Install the UCB library for your programming language
2. Expose or consume APIs using the UCB
3. Test compatibility using the UIP conformance tools

## 3. Installing the Universal Connector Block <a name="installing-the-ucb"></a>

The UCB is available for all major programming languages. Choose the appropriate installation method for your language:

### Python

```bash
pip install universal-connector-block
```

### JavaScript/TypeScript (Node.js)

```bash
npm install universal-connector-block
```

### Java

```xml
<dependency>
  <groupId>org.uip</groupId>
  <artifactId>universal-connector-block</artifactId>
  <version>1.0.0</version>
</dependency>
```

### Go

```bash
go get github.com/uip/universal-connector-block
```

### .NET

```bash
dotnet add package UniversalConnectorBlock
```

### Ruby

```bash
gem install universal_connector_block
```

## 4. Basic Usage <a name="basic-usage"></a>

Once you've installed the UCB, you can start using it to standardize your APIs and integrate with other systems. Here are the basic steps:

### Creating a UCB Instance

```python
# Python example
from universal_connector_block import UniversalConnectorBlock

# Create a UCB instance for your application
ucb = UniversalConnectorBlock(
    app_name="YourApp",
    version="1.0.0",
    base_path="/api/v1"
)
```

### Registering API Endpoints

```python
# Python example
from universal_connector_block import HttpMethod

# Define a handler function
def get_user(user_id: str):
    # Your implementation to fetch a user
    return {"id": user_id, "name": "Example User"}

# Register the endpoint with the UCB
ucb.register_endpoint(
    path="/users/{user_id}",
    method=HttpMethod.GET,
    handler=get_user,
    description="Get a user by ID"
)
```

### Standardizing Data

```python
# Python example
# Convert native data to USS format
user_data = {"id": "123", "name": "Example User"}
universal_data = ucb.standardize_output(user_data)

# Convert USS data back to native format
uss_data = '{"data": {"id": "123", "name": "Example User"}, "metadata": {"type": "Object"}}'
native_data = ucb.translate_input(uss_data)
```

### Exposing API Description

```python
# Python example
# Generate and expose USS-compliant API descriptor
descriptor = ucb.expose_descriptor()

# You can serve this as JSON from an endpoint
# to enable automatic discovery
```

## 5. Creating Self-Describing APIs <a name="self-describing-apis"></a>

A key feature of UIP is the ability to create self-describing APIs that can be automatically discovered and integrated with. Here's how to expose your API description:

### Exposing a Discovery Endpoint

```python
# Python example with Flask
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/.well-known/uip-descriptor.json')
def expose_descriptor():
    return jsonify(json.loads(ucb.expose_descriptor()))
```

### Including Detailed Type Information

When registering endpoints, provide detailed type information to improve integration quality:

```python
# Python example
from typing import List, Dict, Optional

# Define a more complex endpoint with detailed types
def search_products(
    query: str,
    category: Optional[str] = None,
    limit: int = 10,
    offset: int = 0
) -> Dict[str, object]:
    # Implementation...
    return {
        "results": [...],
        "total": 42,
        "limit": limit,
        "offset": offset
    }

ucb.register_endpoint(
    path="/products/search",
    method=HttpMethod.GET,
    handler=search_products,
    description="Search for products"
)
```

### Supporting Schema Evolution

Include versioning information in your API to support backward compatibility:

```python
# Version your UCB instance
ucb_v1 = UniversalConnectorBlock(
    app_name="YourApp",
    version="1.0.0",
    base_path="/api/v1"
)

ucb_v2 = UniversalConnectorBlock(
    app_name="YourApp",
    version="2.0.0",
    base_path="/api/v2"
)
```

## 6. Consuming External APIs <a name="consuming-external-apis"></a>

The UCB makes it easy to consume external APIs with built-in resilience patterns:

### Discovering External APIs

```python
# Python example
import json
import requests

# Fetch API descriptor from a UIP-compatible service
response = requests.get("https://api.example.com/.well-known/uip-descriptor.json")
descriptor = json.loads(response.text)

# Now you can analyze the descriptor to understand the API
endpoints = descriptor["endpoints"]
for endpoint in endpoints:
    print(f"Found endpoint: {endpoint['method']} {endpoint['path']}")
```

### Calling External APIs with Resilience

```python
# Python example
try:
    # Call an external API with retry, circuit breaker, and caching
    result = ucb.call_remote_api(
        url="https://api.example.com/users/123",
        method="GET",
        auth={
            "type": "bearer",
            "token": "your-auth-token"
        },
        use_cache=True,
        retry_attempts=3,
        timeout=30
    )
    
    print("User data:", result)
    
except UcbError as e:
    print(f"API call failed: {e.error_code} - {e.message}")
```

### Type-Safe API Consumption

```python
# Python example
# Define the expected response type
from typing import TypedDict, List

class Product(TypedDict):
    id: str
    name: str
    price: float
    
class SearchResponse(TypedDict):
    results: List[Product]
    total: int

# Make a typed API call
search_result: SearchResponse = ucb.call_remote_api(
    url="https://api.example.com/products/search",
    params={"query": "phone", "limit": 5}
)

# Now you have type-safe access to the response
for product in search_result["results"]:
    print(f"Product: {product['name']} - ${product['price']}")
```

## 7. Advanced Features <a name="advanced-features"></a>

UIP includes several advanced features for complex integration scenarios:

### Custom Type Mapping

```python
# Python example
from universal_connector_block import TypeMapper

# Register a custom type mapper for complex types
class CustomTypeMapper(TypeMapper):
    def python_to_uss(self, py_type):
        if py_type.__name__ == "YourCustomClass":
            return "CustomType"
        return super().python_to_uss(py_type)
        
    def validate_and_convert(self, value, uss_type):
        if uss_type == "CustomType":
            # Custom validation and conversion logic
            return YourCustomClass.from_dict(value)
        return super().validate_and_convert(value, uss_type)

# Use the custom type mapper
ucb.type_mapper = CustomTypeMapper()
```

### Implementing Custom Authentication

```python
# Python example
from universal_connector_block import AuthMethod

# Define a custom authentication method
custom_auth = {
    "type": "custom",
    "handler": lambda req: {
        "X-Custom-Auth": f"Method={compute_hash(req)}",
        "X-Timestamp": int(time.time())
    }
}

# Use the custom auth method
result = ucb.call_remote_api(
    url="https://api.example.com/secure-endpoint",
    auth=custom_auth
)
```

### Event-Driven Integration

```python
# Python example
# Subscribe to events from another system
ucb.subscribe_to_events(
    source_url="https://events.example.com/stream",
    event_types=["user.created", "user.updated"],
    handler=lambda event: process_user_event(event)
)

# Publish events for other systems
ucb.publish_event(
    event_type="order.created",
    payload={"order_id": "123", "total": 99.99},
    destination="https://partner-api.example.com/webhooks/orders"
)
```

## 8. Best Practices <a name="best-practices"></a>

Follow these best practices to get the most out of UIP:

### Type Safety

- Always use strong typing in your API definitions
- Provide detailed type information for parameters and return values
- Use validation to ensure data integrity

### Error Handling

- Include detailed error information in responses
- Use standard error codes defined in the UIP specification
- Implement proper error propagation across system boundaries

### Performance Optimization

- Use caching for frequently accessed data
- Implement pagination for large datasets
- Monitor and optimize response times

### Security

- Always use HTTPS for UIP communication
- Implement proper authentication and authorization
- Follow the principle of least privilege

### Testing

- Use the UIP conformance test suite to validate your implementation
- Implement integration tests for all your UCB-enabled endpoints
- Test resilience patterns with simulated failures

## 9. Troubleshooting <a name="troubleshooting"></a>

Here are solutions to common issues you might encounter:

### Type Conversion Errors

**Problem:** Data fails to convert between native and USS formats.

**Solution:** 
- Ensure your data matches the declared types
- Check for null values if the type doesn't allow them
- Use the UCB's validation helpers to catch issues early

### Connection Failures

**Problem:** API calls fail with connection errors.

**Solution:**
- Verify network connectivity
- Check URL and port configurations
- Ensure proper TLS/SSL setup
- Verify that the circuit breaker isn't open

### Authentication Issues

**Problem:** API calls fail with authentication errors.

**Solution:**
- Check authentication credentials
- Verify token expiration
- Ensure proper authorization scope
- Check for clock skew issues

### Performance Problems

**Problem:** API integration is slow or unresponsive.

**Solution:**
- Enable caching for read operations
- Implement pagination for large datasets
- Check for network latency issues
- Monitor and optimize database queries

## 10. Appendix: Language-Specific Considerations <a name="appendix-language-specific"></a>

### Python

- Use type hints (`typing` module) for best results
- Consider using dataclasses for structured data
- For async applications, use the `universal_connector_block.aio` module

### JavaScript/TypeScript

- TypeScript provides better type safety than JavaScript
- Use interfaces to define your data structures
- For Node.js, use the `universal-connector-block` package
- For browsers, use the `universal-connector-block-web` package

### Java

- Use the `org.uip.ucb` package
- Leverage Java's strong typing system
- Consider using Spring Boot integration for web applications

### Go

- Use the `github.com/uip/ucb` package
- Take advantage of Go's struct tags for field mapping
- Consider using context support for request handling

### .NET

- Use the `UniversalConnectorBlock` NuGet package
- Leverage C# attributes for metadata
- Consider using the ASP.NET Core integration

---

For more information, visit [Universal Integration Protocol](https://uip.org) or contact support@uip.org.

© 2025 Universal Integration Protocol Consortium
