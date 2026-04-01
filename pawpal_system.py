"""
PawPal+ System - Backend Logic Layer

This module contains the core classes for the PawPal+ pet care planning system.
"""

from dataclasses import dataclass, field
from typing import List


# Priority weights for scheduling (higher = more important)
PRIORITY_WEIGHTS = {"high": 3, "medium": 2, "low": 1}


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
            reason = f"Priority: {task.priority}"
            lines.append(f"{i}. {task.title} for {task.pet_name} ({task.duration_minutes}min) - {reason}")

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
