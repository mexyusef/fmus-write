from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Union
import json
import uuid
from datetime import datetime


class BaseModel:
    """Base class for all content models in FMUS-Write."""

    def __init__(self, id: Optional[str] = None):
        self.id = id or str(uuid.uuid4())
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at

    def update(self):
        """Update the last modified timestamp."""
        self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert the model to a dictionary."""
        return {
            "id": self.id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """Create a model instance from a dictionary."""
        instance = cls(id=data.get("id"))
        instance.created_at = data.get("created_at", instance.created_at)
        instance.updated_at = data.get("updated_at", instance.updated_at)
        return instance

    def to_json(self) -> str:
        """Convert the model to a JSON string."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> 'BaseModel':
        """Create a model instance from a JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
