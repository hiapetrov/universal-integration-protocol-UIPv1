"""
Basic usage example for the Universal Connector Block (Python)

This example demonstrates the core functionality of the UCB:
- Creating a UCB instance
- Registering API endpoints
- Standardizing data
- Translating data
- Handling requests
- Calling remote APIs
"""

from universal_connector_block import (
    UniversalConnectorBlock,
    HttpMethod,
    UcbError,
    ValidationError
)

import json
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ucb-example")


def main():
    # Create a UCB instance
    ucb = UniversalConnectorBlock(
        app_name="ExampleApp",
        version="1.0.0",
        base_path="/api/v1"
    )
    
    # Define handler functions for our API endpoints
    def get_user(user_id: str):
        """Get a user by ID."""
        # In a real app, this would fetch data from a database
        return {
            "id": user_id,
            "name": f"User {user_id}",
            "email": f"user{user_id}@example.com",
            "role": "user"
        }
    
    def list_users(limit: int = 10, offset: int = 0):
        """Get a list of users."""
        # In a real app, this would fetch data from a database
        return {
            "users": [
                {
                    "id": str(i),
                    "name": f"User {i}",
                    "email": f"user{i}@example.com"
                }
                for i in range(offset, offset + limit)
            ],
            "total": 100,
            "limit": limit,
            "offset": offset
        }
    
    def create_user(name: str, email: str, role: str = "user"):
        """Create a new user."""
        # In a real app, this would insert data into a database
        return {
            "id": "new-123",
            "name": name,
            "email": email,
            "role": role,
            "created": True
        }
    
    # Register endpoints
    ucb.register_endpoint(
        path="/users/{user_id}",
        method=HttpMethod.GET,
        handler=get_user,
        description="Get a user by ID"
    )
    
    ucb.register_endpoint(
        path="/users",
        method=HttpMethod.GET,
        handler=list_users,
        description="List users with pagination"
    )
    
    ucb.register_endpoint(
        path="/users",
        method=HttpMethod.POST,
        handler=create_user,
        description="Create a new user"
    )
    
    # Generate and print API descriptor
    descriptor = ucb.generate_descriptor()
    logger.info(f"API Descriptor: {json.dumps(descriptor, indent=2)}")
    
    # Example 1: Data standardization
    logger.info("\n=== Example 1: Data Standardization ===")
    user_data = {
        "id": "123",
        "name": "John Doe",
        "email": "john@example.com",
        "role": "admin"
    }
    logger.info(f"Original data: {user_data}")
    
    # Convert to USS format
    universal_data = ucb.standardize_output(user_data)
    logger.info(f"Standardized data: {universal_data}")
    
    # Convert back to native format
    native_data = ucb.translate_input(universal_data)
    logger.info(f"Translated data: {native_data}")
    
    # Example 2: Handling requests
    logger.info("\n=== Example 2: Handling Requests ===")
    try:
        # Simulate a GET request to /users/123
        result = ucb.handle_request(
            path="/users/123",
            method="GET",
            headers={"Authorization": "Bearer test-token"}
        )
        logger.info(f"GET /users/123 result: {result}")
        
        # Simulate a GET request to /users with query parameters
        result = ucb.handle_request(
            path="/users",
            method="GET",
            params={"limit": "5", "offset": "10"},
            headers={"Authorization": "Bearer test-token"}
        )
        logger.info(f"GET /users result: {json.dumps(result, indent=2)}")
        
        # Simulate a POST request to /users
        result = ucb.handle_request(
            path="/users",
            method="POST",
            params={
                "__body": {
                    "name": "Jane Smith",
                    "email": "jane@example.com",
                    "role": "manager"
                }
            },
            headers={"Authorization": "Bearer test-token"}
        )
        logger.info(f"POST /users result: {json.dumps(result, indent=2)}")
        
        # Try an endpoint that doesn't exist
        result = ucb.handle_request(
            path="/not-found",
            method="GET",
            headers={"Authorization": "Bearer test-token"}
        )
    except UcbError as e:
        logger.error(f"Request error: {e.error_code} - {e.message}")
    
    # Example 3: Calling remote APIs (mocked for this example)
    logger.info("\n=== Example 3: Remote API Calls ===")
    try:
        # This would normally call a real API
        # For demo purposes, we'll just log what would happen
        logger.info("Would call remote API: https://api.example.com/users/123")
        logger.info("With retry_attempts=3, timeout=10, auth=Bearer token")
        
        # Result would be something like:
        mock_result = {
            "id": "123",
            "name": "Remote User",
            "email": "remote@example.com"
        }
        logger.info(f"Mock API result: {mock_result}")
    except Exception as e:
        logger.error(f"API call error: {str(e)}")


if __name__ == "__main__":
    main()
