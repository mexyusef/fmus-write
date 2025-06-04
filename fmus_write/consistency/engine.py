"""
Consistency checking engine for FMUS-Write.
"""

from typing import Dict, Any, List, Optional, Callable
import logging
import json
from .validator import ConsistencyValidator, ValidationRule

logger = logging.getLogger(__name__)


class ConsistencyIssue:
    """A detected consistency issue in a story."""

    def __init__(
        self,
        issue_type: str,
        severity: str,
        message: str,
        location: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a consistency issue.

        Args:
            issue_type: Type of consistency issue
            severity: Severity level (critical, major, minor)
            message: Description of the issue
            location: Where the issue occurs (chapter, paragraph, etc.)
            context: Additional context for the issue
        """
        self.issue_type = issue_type
        self.severity = severity
        self.message = message
        self.location = location or {}
        self.context = context or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert issue to dictionary."""
        return {
            "type": self.issue_type,
            "severity": self.severity,
            "message": self.message,
            "location": self.location,
            "context": self.context
        }

    def __str__(self) -> str:
        """String representation of the issue."""
        location_str = ""
        if self.location:
            loc_parts = []
            for k, v in self.location.items():
                loc_parts.append(f"{k}: {v}")
            location_str = f" at {', '.join(loc_parts)}"

        return f"[{self.severity.upper()}] {self.issue_type}: {self.message}{location_str}"


class ConsistencyEngine:
    """Engine for checking story consistency."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the consistency engine.

        Args:
            config: Configuration options
        """
        self.config = config or {
            "character_check_enabled": True,
            "plot_check_enabled": True,
            "world_check_enabled": True,
            "timeline_check_enabled": True,
            "check_threshold": "minor"  # critical, major, minor
        }
        self.checkers: Dict[str, Callable] = {
            "character": self._check_character_consistency,
            "plot": self._check_plot_consistency,
            "world": self._check_world_consistency,
            "timeline": self._check_timeline_consistency
        }
        self.issues: List[ConsistencyIssue] = []
        self.validator = ConsistencyValidator.create_default()
        self.auto_fix_enabled = False
        self.fix_handlers: Dict[str, Callable] = {}

    def validate(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate data for consistency issues.

        Args:
            data: The data to validate

        Returns:
            A list of validation issues found
        """
        logger.info("Running consistency validation")
        issues = self.validator.validate(data)
        logger.info(f"Found {len(issues)} consistency issues")
        return issues

    def register_fix_handler(self, rule_name: str, handler: Callable):
        """Register a handler for fixing issues with a specific rule.

        Args:
            rule_name: The name of the rule to handle
            handler: A function that takes (data, issue) and returns updated data
        """
        self.fix_handlers[rule_name] = handler
        logger.debug(f"Registered fix handler for rule: {rule_name}")

    def enable_auto_fix(self, enabled: bool = True):
        """Enable or disable automatic fixing of issues.

        Args:
            enabled: Whether auto-fixing should be enabled
        """
        self.auto_fix_enabled = enabled
        logger.info(f"Auto-fix {'enabled' if enabled else 'disabled'}")

    def fix_issue(self, data: Dict[str, Any], issue: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to fix a single consistency issue.

        Args:
            data: The data containing the issue
            issue: The issue to fix

        Returns:
            Updated data with the issue fixed (if possible)
        """
        rule_name = issue.get("rule")

        if rule_name in self.fix_handlers:
            logger.info(f"Applying fix for issue: {issue['message']}")
            try:
                updated_data = self.fix_handlers[rule_name](data, issue)
                return updated_data
            except Exception as e:
                logger.error(f"Error fixing issue: {str(e)}")
                return data
        else:
            logger.warning(f"No fix handler for rule: {rule_name}")
            return data

    def fix_issues(self, data: Dict[str, Any], issues: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Attempt to fix all consistency issues.

        Args:
            data: The data containing issues
            issues: List of issues to fix (if None, will run validation)

        Returns:
            Updated data with issues fixed (if possible)
        """
        if issues is None:
            issues = self.validate(data)

        if not issues:
            return data

        updated_data = data.copy()
        fixed_count = 0

        for issue in issues:
            if issue["severity"] == "error" or self.auto_fix_enabled:
                before_fix = updated_data.copy()
                updated_data = self.fix_issue(updated_data, issue)

                # Check if the data was actually changed
                if updated_data != before_fix:
                    fixed_count += 1

        logger.info(f"Fixed {fixed_count} out of {len(issues)} issues")
        return updated_data

    def add_rule(self, rule: ValidationRule):
        """Add a validation rule to the validator.

        Args:
            rule: The rule to add
        """
        self.validator.add_rule(rule)
        logger.debug(f"Added validation rule: {rule.name}")

    def process(self, data: Dict[str, Any], auto_fix: bool = False) -> Dict[str, Any]:
        """Process data through the consistency engine.

        This is the main entry point for using the consistency engine.

        Args:
            data: The data to process
            auto_fix: Whether to automatically fix issues

        Returns:
            A tuple of (updated data, list of remaining issues)
        """
        # Save the current auto-fix setting
        previous_auto_fix = self.auto_fix_enabled

        # Set the auto-fix setting for this run
        self.enable_auto_fix(auto_fix)

        # Validate the data
        issues = self.validate(data)

        # Fix issues if needed
        if issues and (auto_fix or any(issue["severity"] == "error" for issue in issues)):
            updated_data = self.fix_issues(data, issues)

            # Re-validate to find remaining issues
            remaining_issues = self.validate(updated_data)
        else:
            updated_data = data
            remaining_issues = issues

        # Restore the previous auto-fix setting
        self.enable_auto_fix(previous_auto_fix)

        return {
            "data": updated_data,
            "issues": remaining_issues,
            "fixed_count": len(issues) - len(remaining_issues),
            "total_issues": len(issues)
        }

    def check_story(self, story_data: Dict[str, Any]) -> List[ConsistencyIssue]:
        """
        Check the consistency of a story.

        Args:
            story_data: The story data to check

        Returns:
            List[ConsistencyIssue]: Detected consistency issues
        """
        self.issues = []

        # Run enabled checkers
        if self.config.get("character_check_enabled", True):
            self._check_character_consistency(story_data)

        if self.config.get("plot_check_enabled", True):
            self._check_plot_consistency(story_data)

        if self.config.get("world_check_enabled", True):
            self._check_world_consistency(story_data)

        if self.config.get("timeline_check_enabled", True):
            self._check_timeline_consistency(story_data)

        # Filter issues by threshold
        threshold = self.config.get("check_threshold", "minor")
        severity_levels = {
            "critical": 3,
            "major": 2,
            "minor": 1
        }
        threshold_level = severity_levels.get(threshold, 1)

        filtered_issues = [
            issue for issue in self.issues
            if severity_levels.get(issue.severity, 0) >= threshold_level
        ]

        return filtered_issues

    def _check_character_consistency(self, story_data: Dict[str, Any]) -> None:
        """
        Check character consistency across the story.

        Args:
            story_data: The story data
        """
        # Get characters, handling both flat list and nested dict formats
        characters_data = story_data.get("characters", [])

        # Handle the case where characters are in a nested structure
        if isinstance(characters_data, dict) and "characters" in characters_data:
            characters = characters_data.get("characters", [])
        else:
            characters = characters_data

        # Skip if no characters are found
        if not characters:
            return

        # Skip if characters is a string or not iterable
        if isinstance(characters, str) or not hasattr(characters, '__iter__'):
            return

        # Create set of character names for reference
        character_names = set()
        for char in characters:
            if isinstance(char, dict):
                name = char.get("name", "").lower()
                if name:
                    character_names.add(name)
            elif isinstance(char, str):
                character_names.add(char.lower())

        chapters = story_data.get("chapters", [])

        for chapter_idx, chapter in enumerate(chapters):
            content = chapter.get("content", "")

            # Simple check for undefined character mentions
            words = content.split()
            for i, word in enumerate(words):
                # Check for capitalized words that might be names
                if (
                    word
                    and word[0].isupper()
                    and len(word) > 1
                    and word.lower() not in character_names
                    and not any(c in word for c in ",.?!:;-")
                ):
                    # Check if it appears multiple times
                    occurrences = content.lower().count(word.lower())
                    if occurrences > 2:
                        self.issues.append(ConsistencyIssue(
                            issue_type="undefined_character",
                            severity="minor",
                            message=f"Possible undefined character: '{word}' appears {occurrences} times",
                            location={"chapter": chapter_idx + 1},
                            context={"word": word, "occurrences": occurrences}
                        ))

    def _check_plot_consistency(self, story_data: Dict[str, Any]) -> None:
        """
        Check plot consistency across the story.

        Args:
            story_data: The story data
        """
        plot_points = story_data.get("plot_points", [])
        chapters = story_data.get("chapters", [])

        # Example: check for unresolved plot points
        resolved_points = set()
        for chapter in chapters:
            content = chapter.get("content", "")
            for plot_point in plot_points:
                plot_desc = plot_point.get("description", "").lower()
                if plot_desc and plot_desc in content.lower():
                    resolved_points.add(plot_point.get("title"))

        unresolved = [
            plot for plot in plot_points
            if plot.get("title") not in resolved_points
            and plot.get("position") != "background"
        ]

        for unresolved_plot in unresolved:
            self.issues.append(ConsistencyIssue(
                issue_type="unresolved_plot_point",
                severity="major",
                message=f"Unresolved plot point: {unresolved_plot.get('title')}",
                context={"plot_point": unresolved_plot}
            ))

    def _check_world_consistency(self, story_data: Dict[str, Any]) -> None:
        """
        Check world-building consistency across the story.

        Args:
            story_data: The story data
        """
        world = story_data.get("world", {})
        world_rules = world.get("rules", [])
        chapters = story_data.get("chapters", [])

        # Example: check for rule violations
        for chapter_idx, chapter in enumerate(chapters):
            content = chapter.get("content", "")
            for rule in world_rules:
                rule_desc = rule.get("description", "").lower()
                rule_name = rule.get("name", "")

                # Simple check for contradictions
                if rule_desc and "not" in rule_desc:
                    rule_parts = rule_desc.split("not")
                    if len(rule_parts) > 1:
                        forbidden = rule_parts[1].strip()
                        if forbidden and forbidden in content.lower():
                            self.issues.append(ConsistencyIssue(
                                issue_type="world_rule_violation",
                                severity="major",
                                message=f"Possible violation of world rule: {rule_name}",
                                location={"chapter": chapter_idx + 1},
                                context={"rule": rule}
                            ))

    def _check_timeline_consistency(self, story_data: Dict[str, Any]) -> None:
        """
        Check timeline consistency across the story.

        Args:
            story_data: The story data
        """
        chapters = story_data.get("chapters", [])

        # Example: check for time markers in reverse
        time_markers = ["later", "next day", "tomorrow", "next week", "next month", "next year"]

        for chapter_idx in range(len(chapters) - 1):
            current = chapters[chapter_idx].get("content", "").lower()
            next_chapter = chapters[chapter_idx + 1].get("content", "").lower()

            for marker in time_markers:
                if marker in current and "previous" in next_chapter:
                    self.issues.append(ConsistencyIssue(
                        issue_type="timeline_inconsistency",
                        severity="major",
                        message=f"Possible timeline inconsistency between chapters {chapter_idx + 1} and {chapter_idx + 2}",
                        location={"chapters": [chapter_idx + 1, chapter_idx + 2]},
                        context={"forward_marker": marker}
                    ))

    def configure(self, config: Dict[str, Any]) -> None:
        """
        Update the engine configuration.

        Args:
            config: New configuration options
        """
        self.config.update(config)
        logger.debug("Updated consistency engine configuration")

    def get_issues(self) -> List[ConsistencyIssue]:
        """
        Get all detected issues.

        Returns:
            List[ConsistencyIssue]: All detected issues
        """
        return self.issues

    def get_report(self, format_type: str = "text") -> str:
        """
        Generate a report of consistency issues.

        Args:
            format_type: Report format (text, json)

        Returns:
            str: Formatted report
        """
        if format_type == "json":
            return json.dumps([issue.to_dict() for issue in self.issues], indent=2)
        else:
            if not self.issues:
                return "No consistency issues found."

            lines = ["Consistency Check Report:", ""]
            for issue in self.issues:
                lines.append(str(issue))

            return "\n".join(lines)
