"""
Flask integration example for the Universal Connector Block

This example demonstrates how to integrate the UCB with a Flask application.
"""

from flask import Flask, request, jsonify
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
logger = logging.getLogger("ucb-flask-example")

# Create Flask app
app = Flask(__name__)

# Create UCB instance
ucb = UniversalConnectorBlock(
    app_name="FlaskApp",
    version="1.0.0",
    base_path="/api/v1"
)

# Define handler functions
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

# Expose API descriptor
@app.route('/.well-known/uip-descriptor.json')
def get_descriptor():
    """Expose the USS API descriptor."""
    return jsonify(json.loads(ucb.expose_descriptor()))

# Expose OpenAPI/Swagger documentation
@app.route('/docs/openapi.json')
def get_openapi():
    """Generate and return OpenAPI documentation."""
    from universal_connector_block.tools import convert_to_openapi
    openapi = convert_to_openapi(ucb.generate_descriptor())
    return jsonify(openapi)

# Generate Markdown documentation
@app.route('/docs/api.md')
def get_markdown_docs():
    """Generate and return Markdown documentation."""
    from universal_connector_block.tools import generate_markdown_docs
    docs = generate_markdown_docs(ucb.generate_descriptor())
    return docs, 200, {'Content-Type': 'text/markdown'}

# Create a catch-all route for API requests
@app.route('/api/v1/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def api_handler(path):
    """Handle all API requests by delegating to UCB."""
    try:
        # Extract request data
        path = f"/{path}"
        method = request.method
        params = {}
        
        # Include query parameters
        params.update(request.args.to_dict())
        
        # Include body for POST/PUT
        if request.is_json and request.method in ['POST', 'PUT', 'PATCH']:
            params['__body'] = request.json
            
        # Handle the request through UCB
        result = ucb.handle_request(
            path=path,
            method=method,
            params=params,
            headers=dict(request.headers)
        )
        
        return jsonify(result['data']), 200
    except UcbError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        logger.exception(f"Unexpected error: {str(e)}")
        return jsonify({
            "errorCode": "INTERNAL_ERROR",
            "message": str(e)
        }), 500

# Add a quick UI for API testing
@app.route('/')
def index():
    """Provide a simple UI for API testing."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>UCB Flask Example</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            h1 { color: #333; }
            .endpoint { margin-bottom: 20px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
            button { padding: 5px 10px; background-color: #4CAF50; color: white; border: none; border-radius: 3px; cursor: pointer; }
            input, select { padding: 5px; margin-right: 5px; }
            pre { background-color: #f5f5f5; padding: 10px; border-radius: 3px; overflow-x: auto; }
        </style>
    </head>
    <body>
        <h1>UCB Flask Example</h1>
        
        <div class="endpoint">
            <h3>Get User</h3>
            <input type="text" id="userId" placeholder="User ID" value="123">
            <button onclick="getUser()">Get User</button>
            <pre id="getUserResult"></pre>
        </div>
        
        <div class="endpoint">
            <h3>List Users</h3>
            <input type="number" id="limit" placeholder="Limit" value="5">
            <input type="number" id="offset" placeholder="Offset" value="0">
            <button onclick="listUsers()">List Users</button>
            <pre id="listUsersResult"></pre>
        </div>
        
        <div class="endpoint">
            <h3>Create User</h3>
            <input type="text" id="name" placeholder="Name" value="John Doe">
            <input type="email" id="email" placeholder="Email" value="john@example.com">
            <select id="role">
                <option value="user">User</option>
                <option value="admin">Admin</option>
                <option value="manager">Manager</option>
            </select>
            <button onclick="createUser()">Create User</button>
            <pre id="createUserResult"></pre>
        </div>
        
        <div class="endpoint">
            <h3>API Documentation</h3>
            <a href="/.well-known/uip-descriptor.json" target="_blank">USS Descriptor</a> |
            <a href="/docs/openapi.json" target="_blank">OpenAPI</a> |
            <a href="/docs/api.md" target="_blank">Markdown</a>
        </div>
        
        <script>
            async function fetchAPI(url, method, body = null) {
                const headers = { 'Authorization': 'Bearer test-token' };
                if (body) headers['Content-Type'] = 'application/json';
                
                try {
                    const response = await fetch(url, {
                        method,
                        headers,
                        body: body ? JSON.stringify(body) : null
                    });
                    
                    const data = await response.json();
                    return { success: response.ok, data };
                } catch (error) {
                    return { success: false, data: { error: error.message } };
                }
            }
            
            async function getUser() {
                const userId = document.getElementById('userId').value;
                const result = await fetchAPI(`/api/v1/users/${userId}`, 'GET');
                document.getElementById('getUserResult').textContent = JSON.stringify(result.data, null, 2);
            }
            
            async function listUsers() {
                const limit = document.getElementById('limit').value;
                const offset = document.getElementById('offset').value;
                const result = await fetchAPI(`/api/v1/users?limit=${limit}&offset=${offset}`, 'GET');
                document.getElementById('listUsersResult').textContent = JSON.stringify(result.data, null, 2);
            }
            
            async function createUser() {
                const name = document.getElementById('name').value;
                const email = document.getElementById('email').value;
                const role = document.getElementById('role').value;
                
                const result = await fetchAPI('/api/v1/users', 'POST', { name, email, role });
                document.getElementById('createUserResult').textContent = JSON.stringify(result.data, null, 2);
            }
        </script>
    </body>
    </html>
    """

if __name__ == '__main__':
    # Run the Flask application
    app.run(debug=True, port=5000)
