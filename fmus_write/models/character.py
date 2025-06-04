"""
Character-related models for FMUS-Write.
"""

from typing import Dict, Any, List, Optional
from .base import BaseModel


class Trait(BaseModel):
    """A character trait, ability, or characteristic."""

    def __init__(
        self,
        name: str,
        description: str,
        category: str = "personality",
        strength: int = 5,
        id: Optional[str] = None
    ):
        super().__init__(id)
        self.name = name
        self.description = description
        self.category = category  # personality, physical, skill, etc.
        self.strength = strength  # 1-10 scale

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "strength": self.strength
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Trait':
        instance = super().from_dict(data)
        instance.name = data.get("name", "")
        instance.description = data.get("description", "")
        instance.category = data.get("category", "personality")
        instance.strength = data.get("strength", 5)
        return instance


class Relationship(BaseModel):
    """A relationship between characters."""

    def __init__(
        self,
        character_id: str,
        related_character_id: str,
        relationship_type: str,
        description: str,
        strength: int = 5,
        is_mutual: bool = True,
        id: Optional[str] = None
    ):
        super().__init__(id)
        self.character_id = character_id
        self.related_character_id = related_character_id
        self.relationship_type = relationship_type
        self.description = description
        self.strength = strength  # 1-10 scale
        self.is_mutual = is_mutual

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "character_id": self.character_id,
            "related_character_id": self.related_character_id,
            "relationship_type": self.relationship_type,
            "description": self.description,
            "strength": self.strength,
            "is_mutual": self.is_mutual
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Relationship':
        instance = super().from_dict(data)
        instance.character_id = data.get("character_id", "")
        instance.related_character_id = data.get("related_character_id", "")
        instance.relationship_type = data.get("relationship_type", "")
        instance.description = data.get("description", "")
        instance.strength = data.get("strength", 5)
        instance.is_mutual = data.get("is_mutual", True)
        return instance


class Character(BaseModel):
    """Character model representing a character in a story."""

    def __init__(
        self,
        name: str,
        role: str = "supporting",
        description: str = "",
        traits: Optional[List[str]] = None,
        background: str = "",
        motivation: str = "",
        arc: Optional[Dict[str, Any]] = None,
        relationships: Optional[Dict[str, Dict[str, Any]]] = None,
        **kwargs
    ):
        """
        Initialize a character.

        Args:
            name: The character's name
            role: The character's role (protagonist, antagonist, supporting)
            description: Physical and personality description
            traits: List of character traits
            background: Character's backstory
            motivation: Character's primary motivation
            arc: Character's development arc
            relationships: Character's relationships with other characters
        """
        super().__init__(id=kwargs.get('id'))
        self.name = name
        self.role = role
        self.description = description
        self.traits = traits or []
        self.background = background
        self.motivation = motivation
        self.arc = arc or {}
        self.relationships = relationships or {}

    def add_trait(self, trait: str) -> None:
        """
        Add a trait to the character.

        Args:
            trait: The trait to add
        """
        if trait not in self.traits:
            self.traits.append(trait)

    def add_relationship(self, character_name: str, relationship_type: str, description: str) -> None:
        """
        Add or update a relationship with another character.

        Args:
            character_name: The name of the related character
            relationship_type: Type of relationship (friend, enemy, family, etc.)
            description: Description of the relationship
        """
        self.relationships[character_name] = {
            "type": relationship_type,
            "description": description
        }

    def set_arc(self, arc_type: str, start_state: str, end_state: str, milestones: Optional[List[str]] = None) -> None:
        """
        Set the character's development arc.

        Args:
            arc_type: Type of character arc (redemption, fall, growth, etc.)
            start_state: Initial character state
            end_state: Final character state
            milestones: Key development points
        """
        self.arc = {
            "type": arc_type,
            "start_state": start_state,
            "end_state": end_state,
            "milestones": milestones or []
        }

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "name": self.name,
            "role": self.role,
            "description": self.description,
            "traits": self.traits,
            "background": self.background,
            "motivation": self.motivation,
            "arc": self.arc,
            "relationships": self.relationships
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Character':
        # Create a new instance with just the ID parameter for the BaseModel
        instance = cls(
            name=data.get("name", "Unnamed Character"),
            role=data.get("role", "supporting"),
            description=data.get("description", ""),
            traits=data.get("traits", []),
            background=data.get("background", ""),
            motivation=data.get("motivation", ""),
            arc=data.get("arc", {}),
            relationships=data.get("relationships", {}),
            id=data.get("id")
        )

        # Set timestamps if they exist in the data
        if "created_at" in data:
            instance.created_at = data["created_at"]
        if "updated_at" in data:
            instance.updated_at = data["updated_at"]

        return instance


class CharacterArc(BaseModel):
    """A character's development arc through the story."""

    def __init__(
        self,
        character_id: str,
        starting_state: str,
        ending_state: str,
        key_moments: Optional[List[Dict[str, Any]]] = None,
        id: Optional[str] = None
    ):
        super().__init__(id)
        self.character_id = character_id
        self.starting_state = starting_state
        self.ending_state = ending_state
        self.key_moments = key_moments or []

    def add_key_moment(self, title: str, description: str, position: float, impact: int = 5):
        """Add a key moment to the character arc."""
        self.key_moments.append({
            "title": title,
            "description": description,
            "position": position,  # 0.0 to 1.0 representing position in story
            "impact": impact  # 1-10 scale
        })
        self.update()

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "character_id": self.character_id,
            "starting_state": self.starting_state,
            "ending_state": self.ending_state,
            "key_moments": self.key_moments
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CharacterArc':
        instance = super().from_dict(data)
        instance.character_id = data.get("character_id", "")
        instance.starting_state = data.get("starting_state", "")
        instance.ending_state = data.get("ending_state", "")
        instance.key_moments = data.get("key_moments", [])
        return instance
