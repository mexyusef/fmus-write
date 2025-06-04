from typing import Dict, Any, List, Optional, Callable, Set, Tuple
from abc import ABC, abstractmethod
import re


class ValidationRule(ABC):
    """Base class for validation rules."""

    def __init__(self, name: str, description: str, severity: str = "warning"):
        """Initialize a validation rule.

        Args:
            name: The name of the rule
            description: Description of what the rule checks
            severity: The severity of violations ("error", "warning", "info")
        """
        self.name = name
        self.description = description
        self.severity = severity

    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate data against this rule.

        Args:
            data: The data to validate

        Returns:
            A list of validation issues found
        """
        pass


class CharacterConsistencyRule(ValidationRule):
    """Rule to check character consistency across the story."""

    def __init__(self):
        super().__init__(
            name="character_consistency",
            description="Checks that character traits and behaviors are consistent",
            severity="warning"
        )

    def validate(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate character consistency in the story."""
        issues = []

        # Get characters and chapters
        characters = data.get("characters", {}).get("characters", [])
        chapters = data.get("final_chapters", [])

        if not characters or not chapters:
            return issues

        # Create a map of character names for quick lookup
        character_map = {char["name"]: char for char in characters}

        # Check each chapter for character consistency
        for chapter_idx, chapter in enumerate(chapters):
            content = chapter.get("content", "")

            # Check for each character
            for char_name, char_data in character_map.items():
                # Basic check: is the character mentioned in a way inconsistent with traits?
                traits = [trait["name"].lower() for trait in char_data.get("traits", [])]

                # This is a simplified check - in a real implementation,
                # this would use NLP or LLM-based analysis
                for trait in traits:
                    opposite_pattern = f"{char_name}.*(?:not|never|isn't|wasn't).*{trait}"
                    if re.search(opposite_pattern, content, re.IGNORECASE):
                        issues.append({
                            "rule": self.name,
                            "severity": self.severity,
                            "location": f"Chapter {chapter_idx + 1}",
                            "message": f"Character '{char_name}' may be acting inconsistently with trait '{trait}'",
                            "context": "Character consistency check"
                        })

        return issues


class PlotContinuityRule(ValidationRule):
    """Rule to check plot continuity across chapters."""

    def __init__(self):
        super().__init__(
            name="plot_continuity",
            description="Checks that plot elements maintain continuity across chapters",
            severity="error"
        )

    def validate(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate plot continuity in the story."""
        issues = []

        # Get plot points and chapters
        plot_points = data.get("detailed_plot_points", [])
        chapters = data.get("final_chapters", [])

        if not plot_points or not chapters:
            return issues

        # Sort plot points by position
        sorted_points = sorted(plot_points, key=lambda x: x.get("position", 0))

        # Check if plot points are referenced in the correct order in chapters
        # This is a simplified check - in a real implementation,
        # this would use more sophisticated text analysis
        last_found_idx = -1
        for point_idx, point in enumerate(sorted_points):
            point_title = point.get("title", "").lower()

            # Look for this plot point in chapters
            for chapter_idx, chapter in enumerate(chapters):
                content = chapter.get("content", "").lower()

                if point_title in content:
                    if point_idx < last_found_idx:
                        issues.append({
                            "rule": self.name,
                            "severity": self.severity,
                            "location": f"Chapter {chapter_idx + 1}",
                            "message": f"Plot point '{point_title}' appears out of sequence",
                            "context": "Plot continuity check"
                        })
                    last_found_idx = max(last_found_idx, point_idx)

        return issues


class WorldRuleConsistencyRule(ValidationRule):
    """Rule to check consistency with established world rules."""

    def __init__(self):
        super().__init__(
            name="world_rule_consistency",
            description="Checks that content adheres to established world rules",
            severity="warning"
        )

    def validate(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate adherence to world rules."""
        issues = []

        # Get world rules and chapters
        world = data.get("world", {}).get("world", {})
        rules = world.get("rules", [])
        chapters = data.get("final_chapters", [])

        if not rules or not chapters:
            return issues

        # Check each chapter for world rule consistency
        for chapter_idx, chapter in enumerate(chapters):
            content = chapter.get("content", "")

            # Check for each rule
            for rule in rules:
                rule_name = rule.get("name", "").lower()
                rule_desc = rule.get("description", "").lower()

                # This is a simplified check - in a real implementation,
                # this would use NLP or LLM-based analysis
                # Look for potential contradictions to the rule
                contradiction_pattern = f"(?:despite|against|contrary to|ignoring|breaking).*{rule_name}"
                if re.search(contradiction_pattern, content, re.IGNORECASE):
                    issues.append({
                        "rule": self.name,
                        "severity": self.severity,
                        "location": f"Chapter {chapter_idx + 1}",
                        "message": f"Possible violation of world rule '{rule_name}'",
                        "context": "World rule consistency check"
                    })

        return issues


class TimelineConsistencyRule(ValidationRule):
    """Rule to check timeline consistency."""

    def __init__(self):
        super().__init__(
            name="timeline_consistency",
            description="Checks that events occur in a consistent timeline",
            severity="error"
        )

    def validate(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate timeline consistency."""
        issues = []

        # This would be a more complex implementation in a real system,
        # potentially using NLP to extract and compare temporal references

        # For now, we'll just check for obvious temporal markers that might
        # indicate inconsistency
        chapters = data.get("final_chapters", [])

        if not chapters:
            return issues

        # Simple temporal markers to check
        time_markers = {
            "yesterday": -1,
            "today": 0,
            "tomorrow": 1,
            "last week": -7,
            "next week": 7,
            "last month": -30,
            "next month": 30,
            "last year": -365,
            "next year": 365
        }

        current_time_reference = 0

        for chapter_idx, chapter in enumerate(chapters):
            content = chapter.get("content", "").lower()

            # Check for temporal markers
            for marker, offset in time_markers.items():
                if marker in content:
                    implied_time = current_time_reference + offset

                    # Check if this creates an inconsistency with the current chapter position
                    if (offset < 0 and chapter_idx > 0) or (offset > 0 and chapter_idx < len(chapters) - 1):
                        issues.append({
                            "rule": self.name,
                            "severity": self.severity,
                            "location": f"Chapter {chapter_idx + 1}",
                            "message": f"Temporal reference '{marker}' may create timeline inconsistency",
                            "context": "Timeline consistency check"
                        })

        return issues


class ConsistencyValidator:
    """Main validator class that applies rules to check content consistency."""

    def __init__(self):
        self.rules: List[ValidationRule] = []

    def add_rule(self, rule: ValidationRule):
        """Add a validation rule."""
        self.rules.append(rule)

    def validate(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate data against all rules."""
        all_issues = []

        for rule in self.rules:
            try:
                issues = rule.validate(data)
                all_issues.extend(issues)
            except Exception as e:
                # Log the error and continue with other rules
                all_issues.append({
                    "rule": rule.name,
                    "severity": "error",
                    "location": "Validation system",
                    "message": f"Error applying rule: {str(e)}",
                    "context": "Rule execution error"
                })

        return all_issues

    @classmethod
    def create_default(cls) -> 'ConsistencyValidator':
        """Create a validator with the default set of rules."""
        validator = cls()
        validator.add_rule(CharacterConsistencyRule())
        validator.add_rule(PlotContinuityRule())
        validator.add_rule(WorldRuleConsistencyRule())
        validator.add_rule(TimelineConsistencyRule())
        return validator
