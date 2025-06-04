from typing import Dict, Any, Optional, List
from .base import BaseModel


class Location(BaseModel):
    """A physical location in the story world."""

    def __init__(
        self,
        name: str,
        description: str,
        category: str = "general",
        parent_location_id: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        id: Optional[str] = None
    ):
        super().__init__(id)
        self.name = name
        self.description = description
        self.category = category  # city, building, natural feature, etc.
        self.parent_location_id = parent_location_id
        self.attributes = attributes or {}

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "parent_location_id": self.parent_location_id,
            "attributes": self.attributes
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Location':
        instance = super().from_dict(data)
        instance.name = data.get("name", "")
        instance.description = data.get("description", "")
        instance.category = data.get("category", "general")
        instance.parent_location_id = data.get("parent_location_id")
        instance.attributes = data.get("attributes", {})
        return instance


class WorldRule(BaseModel):
    """A rule or law of the story world."""

    def __init__(
        self,
        name: str,
        description: str,
        category: str = "physical",
        implications: Optional[List[str]] = None,
        id: Optional[str] = None
    ):
        super().__init__(id)
        self.name = name
        self.description = description
        self.category = category  # physical, social, magical, etc.
        self.implications = implications or []

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "implications": self.implications
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorldRule':
        instance = super().from_dict(data)
        instance.name = data.get("name", "")
        instance.description = data.get("description", "")
        instance.category = data.get("category", "physical")
        instance.implications = data.get("implications", [])
        return instance


class Culture(BaseModel):
    """A cultural group in the story world."""

    def __init__(
        self,
        name: str,
        description: str,
        values: Optional[List[str]] = None,
        customs: Optional[List[Dict[str, str]]] = None,
        language_notes: Optional[str] = None,
        id: Optional[str] = None
    ):
        super().__init__(id)
        self.name = name
        self.description = description
        self.values = values or []
        self.customs = customs or []
        self.language_notes = language_notes or ""

    def add_custom(self, name: str, description: str):
        """Add a custom to the culture."""
        self.customs.append({
            "name": name,
            "description": description
        })
        self.update()

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "name": self.name,
            "description": self.description,
            "values": self.values,
            "customs": self.customs,
            "language_notes": self.language_notes
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Culture':
        instance = super().from_dict(data)
        instance.name = data.get("name", "")
        instance.description = data.get("description", "")
        instance.values = data.get("values", [])
        instance.customs = data.get("customs", [])
        instance.language_notes = data.get("language_notes", "")
        return instance


class World(BaseModel):
    """The overall world or setting of the story."""

    def __init__(
        self,
        name: str,
        description: str,
        genre: str,
        time_period: Optional[str] = None,
        locations: Optional[List[Location]] = None,
        rules: Optional[List[WorldRule]] = None,
        cultures: Optional[List[Culture]] = None,
        history: Optional[str] = None,
        id: Optional[str] = None
    ):
        super().__init__(id)
        self.name = name
        self.description = description
        self.genre = genre
        self.time_period = time_period or ""
        self.locations = locations or []
        self.rules = rules or []
        self.cultures = cultures or []
        self.history = history or ""

    def add_location(self, location: Location):
        """Add a location to the world."""
        self.locations.append(location)
        self.update()

    def add_rule(self, rule: WorldRule):
        """Add a rule to the world."""
        self.rules.append(rule)
        self.update()

    def add_culture(self, culture: Culture):
        """Add a culture to the world."""
        self.cultures.append(culture)
        self.update()

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "name": self.name,
            "description": self.description,
            "genre": self.genre,
            "time_period": self.time_period,
            "locations": [loc.to_dict() for loc in self.locations],
            "rules": [rule.to_dict() for rule in self.rules],
            "cultures": [culture.to_dict() for culture in self.cultures],
            "history": self.history
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'World':
        instance = super().from_dict(data)
        instance.name = data.get("name", "")
        instance.description = data.get("description", "")
        instance.genre = data.get("genre", "")
        instance.time_period = data.get("time_period", "")

        instance.locations = [
            Location.from_dict(loc_data)
            for loc_data in data.get("locations", [])
        ]

        instance.rules = [
            WorldRule.from_dict(rule_data)
            for rule_data in data.get("rules", [])
        ]

        instance.cultures = [
            Culture.from_dict(culture_data)
            for culture_data in data.get("cultures", [])
        ]

        instance.history = data.get("history", "")
        return instance
