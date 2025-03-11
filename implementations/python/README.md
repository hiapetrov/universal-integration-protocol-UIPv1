# Universal Connector Block for Python

This is the Python implementation of the Universal Connector Block (UCB) for the Universal Integration Protocol (UIP).

## Installation

```bash
pip install universal-connector-block
```

## Quick Start

```python
from universal_connector_block import UniversalConnectorBlock, HttpMethod

# Create a UCB instance
ucb = UniversalConnectorBlock(
    app_name="MyApp",
    version="1.0.0",
    base_path="/api/v1"
)

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

# Standardize data
user_data = {"id": "123", "name": "John Doe"}
universal_data = ucb.standardize_output(user_data)
print(universal_data)

# Translate back to native format
native_data = ucb.translate_input(universal_data)
print(native_data)
```

## Features

- **Data Standardization**: Convert between native Python data and USS format
- **Self-Describing APIs**: Generate USS-compliant API descriptors
- **Resilient API Calls**: Built-in circuit breaker, retries, rate limiting and caching
- **Type Conversion**: Comprehensive type mapping and validation
- **Integration with Web Frameworks**: Support for Flask, FastAPI, and Django

## Documentation

For more information, see the [Python Implementation Guide](../../docs/guides/python-implementation-guide.md) and the [API Reference](../../docs/api/python-ucb-api.md).

## Examples

See the [examples directory](../../examples/python/) for complete example applications.

## Development

### Setup Development Environment

```bash
git clone https://github.com/uip-project/python-ucb.git
cd python-ucb
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Build Documentation

```bash
cd docs
sphinx-build -b html source build
```

## License

This project is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.
