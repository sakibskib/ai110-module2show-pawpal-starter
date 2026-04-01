"""
PawPal+ System - Backend Logic Layer

This module contains the core classes for the PawPal+ pet care planning system.
"""

import json
import os
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


# Priority weights for scheduling (higher = more important)
PRIORITY_WEIGHTS = {"high": 3, "medium": 2, "low": 1}

# Emoji mappings for UI display
PRIORITY_EMOJI = {"high": "🔴", "medium": "🟡", "low": "🟢"}
CATEGORY_EMOJI = {
    "walk": "🚶",
    "feeding": "🍽️",
    "meds": "💊",
    "grooming": "✂️",
    "enrichment": "🎾"
}
SPECIES_EMOJI = {"dog": "🐕", "cat": "🐱", "other": "🐾"}


@dataclass
class Task:
    """Represents a pet care task."""
    title: str
    duration_minutes: int
    priority: str  # "low", "medium", "high"
    category: str  # "walk", "feeding", "meds", "grooming", "enrichment"
    pet_name: str = ""  # Which pet this task is for
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def __str__(self) -> str:
        """Return readable string representation."""
        status = "[DONE]" if self.completed else "[    ]"
        return f"{status} {self.title} ({self.pet_name}) - {self.duration_minutes}min [{self.priority}]"

    def to_dict(self) -> Dict[str, Any]:
        """Convert Task to dictionary for JSON serialization."""
        return {
            "title": self.title,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "category": self.category,
            "pet_name": self.pet_name,
            "completed": self.completed
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Create Task from dictionary."""
        return cls(
            title=data["title"],
            duration_minutes=data["duration_minutes"],
            priority=data["priority"],
            category=data["category"],
            pet_name=data.get("pet_name", ""),
            completed=data.get("completed", False)
        )

    def get_priority_emoji(self) -> str:
        """Return emoji for this task's priority."""
        return PRIORITY_EMOJI.get(self.priority, "⚪")

    def get_category_emoji(self) -> str:
        """Return emoji for this task's category."""
        return CATEGORY_EMOJI.get(self.category, "📋")


@dataclass
class Pet:
    """Represents a pet."""
    name: str
    species: str  # "dog", "cat", "other"
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet."""
        task.pet_name = self.name
        self.tasks.append(task)

    def get_tasks(self) -> List[Task]:
        """Return all tasks for this pet."""
        return self.tasks

    def get_incomplete_tasks(self) -> List[Task]:
        """Return only incomplete tasks for this pet."""
        return [task for task in self.tasks if not task.completed]

    def to_dict(self) -> Dict[str, Any]:
        """Convert Pet to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "species": self.species,
            "tasks": [task.to_dict() for task in self.tasks]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Pet":
        """Create Pet from dictionary."""
        pet = cls(name=data["name"], species=data["species"])
        pet.tasks = [Task.from_dict(t) for t in data.get("tasks", [])]
        return pet

    def get_species_emoji(self) -> str:
        """Return emoji for this pet's species."""
        return SPECIES_EMOJI.get(self.species, "🐾")


@dataclass
class Owner:
    """Represents a pet owner."""
    name: str
    available_time_minutes: int = 60
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_pets(self) -> List[Pet]:
        """Return all pets for this owner."""
        return self.pets

    def get_all_tasks(self) -> List[Task]:
        """Return all tasks from all pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks

    def to_dict(self) -> Dict[str, Any]:
        """Convert Owner to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "available_time_minutes": self.available_time_minutes,
            "pets": [pet.to_dict() for pet in self.pets]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Owner":
        """Create Owner from dictionary."""
        owner = cls(
            name=data["name"],
            available_time_minutes=data.get("available_time_minutes", 60)
        )
        owner.pets = [Pet.from_dict(p) for p in data.get("pets", [])]
        return owner

    def save_to_json(self, filepath: str = "data.json") -> None:
        """Save owner data to a JSON file."""
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_json(cls, filepath: str = "data.json") -> Optional["Owner"]:
        """Load owner data from a JSON file. Returns None if file doesn't exist."""
        if not os.path.exists(filepath):
            return None
        with open(filepath, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)


class Scheduler:
    """Handles scheduling of pet care tasks."""

    def __init__(self, owner: Owner):
        """Initialize scheduler with an owner."""
        self.owner = owner
        self.all_tasks: List[Task] = []

    def _collect_all_tasks(self) -> List[Task]:
        """Gather all incomplete tasks from all pets owned by the owner."""
        self.all_tasks = []
        for pet in self.owner.get_pets():
            self.all_tasks.extend(pet.get_incomplete_tasks())
        return self.all_tasks

    def generate_schedule(self) -> List[Task]:
        """
        Generate an optimized daily schedule based on:
        - Available time
        - Task priorities
        - Task durations

        Returns a list of tasks in scheduled order.
        """
        # Collect all incomplete tasks
        self._collect_all_tasks()

        # Sort tasks by priority (high first), then by duration (shorter first)
        sorted_tasks = sorted(
            self.all_tasks,
            key=lambda t: (-PRIORITY_WEIGHTS.get(t.priority, 0), t.duration_minutes)
        )

        # Select tasks that fit within available time
        scheduled = []
        remaining_time = self.owner.available_time_minutes

        for task in sorted_tasks:
            if task.duration_minutes <= remaining_time:
                scheduled.append(task)
                remaining_time -= task.duration_minutes

        return scheduled

    def explain_schedule(self, schedule: List[Task]) -> str:
        """
        Explain why tasks were scheduled in this order.

        Returns a human-readable explanation string.
        """
        if not schedule:
            return "No tasks scheduled. Either all tasks are complete or none fit the available time."

        total_time = self.get_total_time(schedule)
        available = self.owner.available_time_minutes

        lines = [
            f"Schedule for {self.owner.name} ({total_time}/{available} minutes used)",
            "-" * 50
        ]

        for i, task in enumerate(schedule, 1):
            emoji = f"{task.get_priority_emoji()} {task.get_category_emoji()}"
            reason = f"Priority: {task.priority}"
            lines.append(f"{i}. {emoji} {task.title} for {task.pet_name} ({task.duration_minutes}min) - {reason}")

        # Note skipped tasks
        skipped = [t for t in self.all_tasks if t not in schedule]
        if skipped:
            lines.append("")
            lines.append("Skipped (not enough time):")
            for task in skipped:
                lines.append(f"  - {task.title} for {task.pet_name} ({task.duration_minutes}min)")

        return "\n".join(lines)

    def get_total_time(self, tasks: List[Task]) -> int:
        """Calculate total time required for a list of tasks."""
        return sum(task.duration_minutes for task in tasks)
