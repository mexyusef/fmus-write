"""
World and setting related models for FMUS-Write.
"""

from typing import Dict, Any, List, Optional
from .base import BaseModel


class World(BaseModel):
    """World model representing the setting of a story."""

    def __init__(
        self,
        name: str,
        description: str = "",
        time_period: str = "",
        locations: Optional[List[Dict[str, Any]]] = None,
        cultures: Optional[List[Dict[str, Any]]] = None,
        rules: Optional[List[Dict[str, Any]]] = None,
        history: str = "",
        **kwargs
    ):
        """
        Initialize a world.

        Args:
            name: The name of the world/setting
            description: General description of the world
            time_period: The time period or era
            locations: List of locations in the world
            cultures: List of cultures or societies
            rules: List of rules or laws (natural, magical, social)
            history: Brief history of the world
        """
        super().__init__(
            name=name,
            description=description,
            time_period=time_period,
            locations=locations or [],
            cultures=cultures or [],
            rules=rules or [],
            history=history,
            **kwargs
        )

    def add_location(self, name: str, description: str, importance: str = "minor") -> None:
        """
        Add a location to the world.

        Args:
            name: The name of the location
            description: Description of the location
            importance: Importance of the location (major, minor)
        """
        self.locations.append({
            "name": name,
            "description": description,
            "importance": importance
        })

    def add_culture(self, name: str, description: str, values: Optional[List[str]] = None) -> None:
        """
        Add a culture to the world.

        Args:
            name: The name of the culture
            description: Description of the culture
            values: List of cultural values or beliefs
        """
        self.cultures.append({
            "name": name,
            "description": description,
            "values": values or []
        })

    def add_rule(self, name: str, description: str, rule_type: str = "natural") -> None:
        """
        Add a rule to the world.

        Args:
            name: The name of the rule
            description: Description of the rule
            rule_type: Type of rule (natural, magical, social, etc.)
        """
        self.rules.append({
            "name": name,
            "description": description,
            "type": rule_type
        })
