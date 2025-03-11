"""
Utility tools for the Universal Connector Block.
"""

import json
import re
from typing import Dict, Any, List, Optional, Union


def convert_to_openapi(uss_descriptor: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a USS API descriptor to OpenAPI 3.0 format.
    
    Args:
        uss_descriptor: The USS API descriptor
        
    Returns:
        OpenAPI 3.0 specification
    """
    # Basic OpenAPI structure
    openapi_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": uss_descriptor.get("name", "API"),
            "version": uss_descriptor.get("version", "1.0.0"),
            "description": uss_descriptor.get("description", "")
        },
        "servers": [
            {
                "url": f"https://api.example.com{uss_descriptor.get('basePath', '')}",
                "description": "Example server"
            }
        ],
        "paths": {},
        "components": {
            "schemas": {},
            "securitySchemes": {}
        }
    }
    
    # Add security schemes
    openapi_spec["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer"
        },
        "apiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key"
        }
    }
    
    # Process endpoints
    for endpoint in uss_descriptor.get("endpoints", []):
        path = endpoint.get("path", "")
        method = endpoint.get("method", "get").lower()
        
        # Initialize path if not exists
        if path not in openapi_spec["paths"]:
            openapi_spec["paths"][path] = {}
        
        # Add operation
        operation = {
            "summary": endpoint.get("description", ""),
            "parameters": [],
            "responses": {}
        }
        
        # Add parameters
        for param in endpoint.get("parameters", []):
            param_location = param.get("location", "query")
            if param_location == "body":
                # OpenAPI 3.0 uses requestBody instead of body parameter
                continue
                
            openapi_param = {
                "name": param.get("name", ""),
                "in": param_location,
                "required": param.get("required", False),
                "schema": _convert_uss_type_to_openapi(param.get("type", "String"))
            }
            
            if param.get("description"):
                openapi_param["description"] = param.get("description")
                
            operation["parameters"].append(openapi_param)
        
        # Add request body if needed
        body_params = [p for p in endpoint.get("parameters", []) 
                       if p.get("location") == "body"]
        if body_params:
            request_body = {
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                },
                "required": any(p.get("required", False) for p in body_params)
            }
            
            for param in body_params:
                request_body["content"]["application/json"]["schema"]["properties"][param.get("name", "")] = _convert_uss_type_to_openapi(param.get("type", "String"))
                
            operation["requestBody"] = request_body
        
        # Add responses
        for resp in endpoint.get("responses", []):
            status_code = str(resp.get("statusCode", 200))
            operation["responses"][status_code] = {
                "description": resp.get("description", "Response"),
                "content": {
                    resp.get("contentType", "application/json"): {
                        "schema": _convert_schema_to_openapi(resp.get("schema", {}))
                    }
                }
            }
        
        # Add security if required
        if endpoint.get("authentication", {}).get("required", False):
            auth_methods = endpoint.get("authentication", {}).get("methods", [])
            security = []
            
            if "bearer" in auth_methods or "Bearer" in auth_methods:
                security.append({"bearerAuth": []})
                
            if "api_key" in auth_methods or "apiKey" in auth_methods:
                security.append({"apiKeyAuth": []})
                
            if security:
                operation["security"] = security
        
        # Add operation to path
        openapi_spec["paths"][path][method] = operation
    
    return openapi_spec


def _convert_uss_type_to_openapi(uss_type: str) -> Dict[str, Any]:
    """Convert a USS type to OpenAPI schema format."""
    if uss_type == "String":
        return {"type": "string"}
    elif uss_type == "Integer":
        return {"type": "integer"}
    elif uss_type == "Float":
        return {"type": "number"}
    elif uss_type == "Boolean":
        return {"type": "boolean"}
    elif uss_type == "Object":
        return {"type": "object"}
    elif uss_type == "Array":
        return {"type": "array", "items": {"type": "string"}}
    elif uss_type.startswith("Array<"):
        item_type = uss_type[6:-1]
        return {"type": "array", "items": _convert_uss_type_to_openapi(item_type)}
    elif uss_type == "DateTime" or uss_type == "Date":
        return {"type": "string", "format": "date-time"}
    elif uss_type == "Binary":
        return {"type": "string", "format": "binary"}
    elif uss_type == "Null":
        return {"type": "null"}
    else:
        return {"type": "string"}


def _convert_schema_to_openapi(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a USS schema to OpenAPI schema format."""
    if not schema:
        return {"type": "object"}
        
    schema_type = schema.get("type", "Object")
    
    if schema_type == "Object" and "properties" in schema:
        result = {
            "type": "object",
            "properties": {}
        }
        
        for prop_name, prop_schema in schema.get("properties", {}).items():
            result["properties"][prop_name] = _convert_schema_to_openapi(prop_schema)
            
        return result
    else:
        return _convert_uss_type_to_openapi(schema_type)


def generate_markdown_docs(uss_descriptor: Dict[str, Any]) -> str:
    """
    Generate Markdown documentation from a USS API descriptor.
    
    Args:
        uss_descriptor: The USS API descriptor
        
    Returns:
        Markdown formatted documentation
    """
    app_name = uss_descriptor.get("name", "API")
    version = uss_descriptor.get("version", "1.0.0")
    description = uss_descriptor.get("description", "")
    base_path = uss_descriptor.get("basePath", "")
    
    # Start with the header
    markdown = f"# {app_name} API Documentation\n\n"
    
    if description:
        markdown += f"{description}\n\n"
        
    markdown += f"**Version:** {version}  \n"
    markdown += f"**Base Path:** {base_path}\n\n"
    
    # Create table of contents
    markdown += "## Table of Contents\n\n"
    for i, endpoint in enumerate(uss_descriptor.get("endpoints", [])):
        path = endpoint.get("path", "")
        method = endpoint.get("method", "").upper()
        desc = endpoint.get("description", "")
        
        # Create link-friendly name
        link_name = re.sub(r'[^a-zA-Z0-9]+', '-', f"{method}-{path}").lower()
        name = desc if desc else f"{method} {path}"
        
        markdown += f"{i+1}. [{name}](#{link_name})\n"
    
    markdown += "\n## Endpoints\n\n"
    
    # Document each endpoint
    for endpoint in uss_descriptor.get("endpoints", []):
        path = endpoint.get("path", "")
        method = endpoint.get("method", "").upper()
        desc = endpoint.get("description", "")
        
        # Create anchor for TOC
        link_name = re.sub(r'[^a-zA-Z0-9]+', '-', f"{method}-{path}").lower()
        name = desc if desc else f"{method} {path}"
        
        markdown += f"### {name}\n\n"
        markdown += f"**Path:** `{path}`  \n"
        markdown += f"**Method:** `{method}`  \n"
        
        # Authentication
        auth = endpoint.get("authentication", {})
        auth_required = auth.get("required", False)
        auth_methods = auth.get("methods", [])
        
        if auth_required:
            markdown += "**Authentication Required:** Yes  \n"
            if auth_methods:
                markdown += f"**Authentication Methods:** {', '.join(auth_methods)}  \n"
        else:
            markdown += "**Authentication Required:** No  \n"
        
        # Rate limiting
        rate_limit = endpoint.get("rateLimit")
        if rate_limit:
            markdown += f"**Rate Limit:** {rate_limit} requests per minute  \n"
            
        markdown += "\n"
        
        # Parameters
        parameters = endpoint.get("parameters", [])
        if parameters:
            markdown += "#### Parameters\n\n"
            markdown += "| Name | Location | Type | Required | Description |\n"
            markdown += "|------|----------|------|----------|-------------|\n"
            
            for param in parameters:
                name = param.get("name", "")
                location = param.get("location", "query")
                param_type = param.get("type", "String")
                required = "Yes" if param.get("required", False) else "No"
                desc = param.get("description", "")
                
                markdown += f"| {name} | {location} | {param_type} | {required} | {desc} |\n"
                
            markdown += "\n"
            
        # Responses
        responses = endpoint.get("responses", [])
        if responses:
            markdown += "#### Responses\n\n"
            markdown += "| Status Code | Content Type | Description |\n"
            markdown += "|-------------|--------------|-------------|\n"
            
            for resp in responses:
                status = resp.get("statusCode", 200)
                content_type = resp.get("contentType", "application/json")
                desc = resp.get("description", "")
                
                markdown += f"| {status} | {content_type} | {desc} |\n"
                
            markdown += "\n"
            
            # Add response schema examples
            for resp in responses:
                if resp.get("schema"):
                    status = resp.get("statusCode", 200)
                    markdown += f"##### Response Schema ({status})\n\n"
                    markdown += "```json\n"
                    markdown += json.dumps(resp.get("schema"), indent=2)
                    markdown += "\n```\n\n"
        
        # Add example if available
        if endpoint.get("example"):
            markdown += "#### Example\n\n"
            markdown += "```json\n"
            markdown += json.dumps(endpoint.get("example"), indent=2)
            markdown += "\n```\n\n"
    
    return markdown
