"""
Type handling for the Universal Connector Block implementation.
"""

import inspect
import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, get_origin, get_args

from .errors import ValidationError

# Type definitions
T = TypeVar('T')

# Registry for custom type adapters
_TYPE_ADAPTERS = {}


def register_type_adapter(cls: Type[T], serialize_fn=None, deserialize_fn=None):
    """
    Register custom serialization/deserialization functions for a type.
    
    Args:
        cls: The class to register
        serialize_fn: Function to convert instance to serializable form
        deserialize_fn: Function to convert serialized form back to instance
    """
    _TYPE_ADAPTERS[cls] = {
        "serialize": serialize_fn,
        "deserialize": deserialize_fn
    }


class TypeMapper:
    """Maps between Python types and USS types."""
    
    # Mapping from Python types to USS types
    PYTHON_TO_USS = {
        str: "String",
        int: "Integer",
        float: "Float",
        bool: "Boolean",
        dict: "Object",
        list: "Array",
        tuple: "Array",
        set: "Array",
        datetime.datetime: "DateTime",
        datetime.date: "Date",
        bytes: "Binary",
        type(None): "Null"
    }
    
    # Mapping from USS types to Python types
    USS_TO_PYTHON = {
        "String": str,
        "Integer": int,
        "Float": float,
        "Boolean": bool,
        "Object": dict,
        "Array": list,
        "DateTime": datetime.datetime,
        "Date": datetime.date,
        "Binary": bytes,
        "Null": type(None)
    }
    
    def python_to_uss(self, py_type) -> str:
        """Convert Python type to USS type."""
        if py_type in self.PYTHON_TO_USS:
            return self.PYTHON_TO_USS[py_type]
        
        # Handle typing module types
        origin = get_origin(py_type)
        if origin is not None:
            if origin is Union:
                args = get_args(py_type)
                if type(None) in args and len(args) == 2:
                    # This is Optional[T]
                    other_type = next(arg for arg in args if arg is not type(None))
                    return self.python_to_uss(other_type)
                return "Union"
            if origin is list or origin is tuple or origin is set:
                args = get_args(py_type)
                item_type = "Any" if not args else self.python_to_uss(args[0])
                return f"Array<{item_type}>"
            if origin is dict:
                return "Object"
        
        # Dataclasses become Objects
        if hasattr(py_type, "__dataclass_fields__"):
            return "Object"
            
        # For custom registered types
        if py_type in _TYPE_ADAPTERS:
            return "Object"
            
        # Default fallback
        return "Any"
    
    def infer_type_from_value(self, value) -> str:
        """Infer USS type from a Python value."""
        if value is None:
            return "Null"
            
        # Check if the value's type is directly registered
        value_type = type(value)
        if value_type in self.PYTHON_TO_USS:
            return self.PYTHON_TO_USS[value_type]
            
        # Check for custom registered types
        for cls, adapters in _TYPE_ADAPTERS.items():
            if isinstance(value, cls) and adapters.get("serialize"):
                return "Object"
        
        # Handle special cases
        if hasattr(value, "__dataclass_fields__"):
            return "Object"
            
        # Handle collections
        if isinstance(value, (list, tuple, set)):
            if value:
                # Try to determine item type from first item
                item_type = self.infer_type_from_value(value[0])
                return f"Array<{item_type}>"
            return "Array"
            
        # Default fallback
        return "Any"
    
    def validate_and_convert(self, value: Any, uss_type: str) -> Any:
        """Validate and convert a value according to USS type."""
        if uss_type == "Any":
            return value
            
        if uss_type == "Null" and value is not None:
            raise ValidationError("Expected null value", [{"value": value, "expectedType": "Null"}])
            
        if value is None and not uss_type.startswith("Union"):
            raise ValidationError(f"Unexpected null value for type {uss_type}", 
                                 [{"value": None, "expectedType": uss_type}])
                                 
        if uss_type == "String":
            if not isinstance(value, str):
                return str(value)  # Attempt conversion
            return value
            
        if uss_type == "Integer":
            if isinstance(value, int) and not isinstance(value, bool):
                return value
            try:
                return int(value)
            except (ValueError, TypeError):
                raise ValidationError(f"Cannot convert {value} to Integer", 
                                     [{"value": value, "expectedType": "Integer"}])
                                     
        if uss_type == "Float":
            if isinstance(value, float):
                return value
            try:
                return float(value)
            except (ValueError, TypeError):
                raise ValidationError(f"Cannot convert {value} to Float", 
                                     [{"value": value, "expectedType": "Float"}])
                                     
        if uss_type == "Boolean":
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                if value.lower() in ("true", "yes", "1"):
                    return True
                if value.lower() in ("false", "no", "0"):
                    return False
            raise ValidationError(f"Cannot convert {value} to Boolean", 
                                 [{"value": value, "expectedType": "Boolean"}])
                                 
        if uss_type == "Object" and not isinstance(value, dict):
            if hasattr(value, "__dict__"):
                return value.__dict__
            if value.__class__ in _TYPE_ADAPTERS and _TYPE_ADAPTERS[value.__class__].get("serialize"):
                return _TYPE_ADAPTERS[value.__class__]["serialize"](value)
            raise ValidationError(f"Expected Object, got {type(value).__name__}", 
                                 [{"value": value, "expectedType": "Object"}])
                                 
        if uss_type.startswith("Array"):
            if not isinstance(value, (list, tuple, set)):
                raise ValidationError(f"Expected Array, got {type(value).__name__}", 
                                     [{"value": value, "expectedType": "Array"}])
            # If we have Array<Type>, validate each element
            if uss_type != "Array" and "<" in uss_type:
                item_type = uss_type[uss_type.index("<")+1:-1]
                return [self.validate_and_convert(item, item_type) for item in value]
            return list(value)
            
        if uss_type == "DateTime":
            if isinstance(value, datetime.datetime):
                return value
            if isinstance(value, str):
                try:
                    return datetime.datetime.fromisoformat(value)
                except ValueError:
                    pass
            raise ValidationError(f"Cannot convert {value} to DateTime", 
                                 [{"value": value, "expectedType": "DateTime"}])
                                 
        if uss_type == "Date":
            if isinstance(value, datetime.date):
                return value
            if isinstance(value, str):
                try:
                    return datetime.date.fromisoformat(value)
                except ValueError:
                    pass
            raise ValidationError(f"Cannot convert {value} to Date", 
                                 [{"value": value, "expectedType": "Date"}])
            
        # Handle deserializing custom types
        uss_type_class = None
        for cls, adapters in _TYPE_ADAPTERS.items():
            if cls.__name__ == uss_type and adapters.get("deserialize"):
                if isinstance(value, dict):
                    return adapters["deserialize"](value)
                raise ValidationError(f"Cannot convert {type(value).__name__} to {uss_type}", 
                                     [{"value": value, "expectedType": uss_type}])
            
        return value
