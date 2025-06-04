from typing import Dict, Any, Optional, List, Union
from .base import BaseModel


class PlotPoint(BaseModel):
    """A significant event in the story."""

    def __init__(
        self,
        title: str,
        description: str,
        position: float,
        importance: int = 5,
        characters: Optional[List[str]] = None,
        settings: Optional[List[str]] = None,
        id: Optional[str] = None
    ):
        super().__init__(id)
        self.title = title
        self.description = description
        self.position = position  # 0.0 to 1.0 representing position in story
        self.importance = importance  # 1-10 scale
        self.characters = characters or []
        self.settings = settings or []

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "title": self.title,
            "description": self.description,
            "position": self.position,
            "importance": self.importance,
            "characters": self.characters,
            "settings": self.settings
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlotPoint':
        instance = super().from_dict(data)
        instance.title = data.get("title", "")
        instance.description = data.get("description", "")
        instance.position = data.get("position", 0.0)
        instance.importance = data.get("importance", 5)
        instance.characters = data.get("characters", [])
        instance.settings = data.get("settings", [])
        return instance


class Scene(BaseModel):
    """A scene within a chapter."""

    def __init__(
        self,
        title: str,
        description: str,
        content: Optional[str] = None,
        pov_character: Optional[str] = None,
        characters: Optional[List[str]] = None,
        setting: Optional[str] = None,
        plot_points: Optional[List[str]] = None,
        id: Optional[str] = None
    ):
        super().__init__(id)
        self.title = title
        self.description = description
        self.content = content or ""
        self.pov_character = pov_character
        self.characters = characters or []
        self.setting = setting
        self.plot_points = plot_points or []

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "title": self.title,
            "description": self.description,
            "content": self.content,
            "pov_character": self.pov_character,
            "characters": self.characters,
            "setting": self.setting,
            "plot_points": self.plot_points
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Scene':
        instance = super().from_dict(data)
        instance.title = data.get("title", "")
        instance.description = data.get("description", "")
        instance.content = data.get("content", "")
        instance.pov_character = data.get("pov_character")
        instance.characters = data.get("characters", [])
        instance.setting = data.get("setting")
        instance.plot_points = data.get("plot_points", [])
        return instance


class Chapter(BaseModel):
    """A chapter in the book."""

    def __init__(
        self,
        title: str,
        number: int,
        description: Optional[str] = None,
        scenes: Optional[List[Scene]] = None,
        id: Optional[str] = None
    ):
        super().__init__(id)
        self.title = title
        self.number = number
        self.description = description or ""
        self.scenes = scenes or []

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "title": self.title,
            "number": self.number,
            "description": self.description,
            "scenes": [scene.to_dict() for scene in self.scenes]
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Chapter':
        instance = super().from_dict(data)
        instance.title = data.get("title", "")
        instance.number = data.get("number", 0)
        instance.description = data.get("description", "")
        instance.scenes = [Scene.from_dict(scene_data) for scene_data in data.get("scenes", [])]
        return instance


class Timeline(BaseModel):
    """Represents the chronological order of events in the story."""

    def __init__(
        self,
        events: Optional[List[Dict[str, Any]]] = None,
        id: Optional[str] = None
    ):
        super().__init__(id)
        self.events = events or []

    def add_event(self, title: str, description: str, timestamp: str, related_entities: List[str] = None):
        """Add a new event to the timeline."""
        self.events.append({
            "title": title,
            "description": description,
            "timestamp": timestamp,
            "related_entities": related_entities or []
        })
        self.update()

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "events": self.events
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Timeline':
        instance = super().from_dict(data)
        instance.events = data.get("events", [])
        return instance


class StoryStructure(BaseModel):
    """A complete story structure with plot, scenes, chapters, etc."""

    def __init__(
        self,
        title: str,
        genre: str,
        premise: str = "",
        theme: Optional[str] = None,
        plot_points: Optional[List[Dict[str, Any]]] = None,
        chapters: Optional[List[Dict[str, Any]]] = None,
        settings: Optional[Dict[str, Any]] = None,
        id: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize a story structure.

        Args:
            title: The title of the story
            genre: The genre of the story
            premise: A short description of the story premise
            theme: The central theme of the story
            plot_points: A list of major plot points
            chapters: A list of chapter structures
            settings: Additional story settings
            id: Optional ID for the story
        """
        super().__init__(id=id)
        self.title = title
        self.genre = genre
        self.premise = premise
        self.theme = theme or ""
        self.plot_points = plot_points or []
        self.chapters = chapters or []
        self.settings = settings or {}

    def add_chapter(self, title: str, summary: str = "", scenes: Optional[List[Dict[str, Any]]] = None) -> None:
        """
        Add a chapter to the story.

        Args:
            title: The title of the chapter
            summary: A brief summary of the chapter
            scenes: A list of scenes in the chapter
        """
        self.chapters.append({
            "title": title,
            "summary": summary,
            "scenes": scenes or [],
            "content": ""
        })

    def add_plot_point(self, title: str, description: str, position: Optional[str] = None) -> None:
        """
        Add a plot point to the story.

        Args:
            title: The title of the plot point
            description: A description of the plot point
            position: The structural position (e.g., "inciting_incident", "climax")
        """
        self.plot_points.append({
            "title": title,
            "description": description,
            "position": position or "general"
        })

    def get_word_count(self) -> int:
        """
        Calculate the total word count of generated content.

        Returns:
            int: The total word count
        """
        total = 0
        for chapter in self.chapters:
            if "content" in chapter and chapter["content"]:
                total += len(chapter["content"].split())
        return total

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "title": self.title,
            "genre": self.genre,
            "theme": self.theme,
            "premise": self.premise,
            "plot_points": self.plot_points,
            "chapters": self.chapters,
            "settings": self.settings
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StoryStructure':
        instance = super().from_dict(data)
        instance.title = data.get("title", "")
        instance.genre = data.get("genre", "")
        instance.theme = data.get("theme", "")
        instance.premise = data.get("premise", "")
        instance.plot_points = data.get("plot_points", [])
        instance.chapters = data.get("chapters", [])
        instance.settings = data.get("settings", {})
        return instance
