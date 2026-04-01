"""
Tests for PawPal+ System

Run with: python -m pytest
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pawpal_system import Task, Pet, Owner, Scheduler


class TestTask:
    """Tests for the Task class."""

    def test_mark_complete_changes_status(self):
        """Verify that calling mark_complete() actually changes the task's status."""
        task = Task(
            title="Morning walk",
            duration_minutes=30,
            priority="high",
            category="walk"
        )

        # Initially, task should not be completed
        assert task.completed is False

        # After marking complete, status should change
        task.mark_complete()
        assert task.completed is True

    def test_task_has_correct_attributes(self):
        """Verify task stores all attributes correctly."""
        task = Task(
            title="Feed breakfast",
            duration_minutes=10,
            priority="medium",
            category="feeding",
            pet_name="Mochi"
        )

        assert task.title == "Feed breakfast"
        assert task.duration_minutes == 10
        assert task.priority == "medium"
        assert task.category == "feeding"
        assert task.pet_name == "Mochi"


class TestPet:
    """Tests for the Pet class."""

    def test_add_task_increases_task_count(self):
        """Verify that adding a task to a Pet increases that pet's task count."""
        pet = Pet(name="Mochi", species="dog")

        # Initially, pet should have no tasks
        assert len(pet.get_tasks()) == 0

        # Add a task
        task = Task(
            title="Morning walk",
            duration_minutes=30,
            priority="high",
            category="walk"
        )
        pet.add_task(task)

        # Task count should increase
        assert len(pet.get_tasks()) == 1

        # Add another task
        task2 = Task(
            title="Brush fur",
            duration_minutes=15,
            priority="low",
            category="grooming"
        )
        pet.add_task(task2)

        # Task count should be 2
        assert len(pet.get_tasks()) == 2

    def test_add_task_sets_pet_name(self):
        """Verify that adding a task automatically sets the pet_name."""
        pet = Pet(name="Whiskers", species="cat")
        task = Task(
            title="Feed",
            duration_minutes=5,
            priority="high",
            category="feeding"
        )

        pet.add_task(task)
        assert task.pet_name == "Whiskers"

    def test_get_incomplete_tasks(self):
        """Verify that get_incomplete_tasks filters out completed tasks."""
        pet = Pet(name="Mochi", species="dog")

        task1 = Task(title="Walk", duration_minutes=30, priority="high", category="walk")
        task2 = Task(title="Feed", duration_minutes=10, priority="high", category="feeding")

        pet.add_task(task1)
        pet.add_task(task2)

        # Both tasks incomplete
        assert len(pet.get_incomplete_tasks()) == 2

        # Mark one complete
        task1.mark_complete()
        assert len(pet.get_incomplete_tasks()) == 1
        assert pet.get_incomplete_tasks()[0].title == "Feed"


class TestOwner:
    """Tests for the Owner class."""

    def test_add_pet(self):
        """Verify that adding pets works correctly."""
        owner = Owner(name="Jordan")

        assert len(owner.get_pets()) == 0

        pet = Pet(name="Mochi", species="dog")
        owner.add_pet(pet)

        assert len(owner.get_pets()) == 1
        assert owner.get_pets()[0].name == "Mochi"

    def test_get_all_tasks(self):
        """Verify owner can retrieve all tasks from all pets."""
        owner = Owner(name="Jordan")

        pet1 = Pet(name="Mochi", species="dog")
        pet2 = Pet(name="Whiskers", species="cat")

        pet1.add_task(Task(title="Walk", duration_minutes=30, priority="high", category="walk"))
        pet2.add_task(Task(title="Feed", duration_minutes=10, priority="high", category="feeding"))
        pet2.add_task(Task(title="Play", duration_minutes=15, priority="medium", category="enrichment"))

        owner.add_pet(pet1)
        owner.add_pet(pet2)

        all_tasks = owner.get_all_tasks()
        assert len(all_tasks) == 3


class TestScheduler:
    """Tests for the Scheduler class."""

    def test_generate_schedule_respects_time_limit(self):
        """Verify scheduler doesn't exceed available time."""
        owner = Owner(name="Jordan", available_time_minutes=30)
        pet = Pet(name="Mochi", species="dog")

        pet.add_task(Task(title="Walk", duration_minutes=20, priority="high", category="walk"))
        pet.add_task(Task(title="Groom", duration_minutes=20, priority="low", category="grooming"))

        owner.add_pet(pet)

        scheduler = Scheduler(owner)
        schedule = scheduler.generate_schedule()

        total_time = scheduler.get_total_time(schedule)
        assert total_time <= owner.available_time_minutes

    def test_generate_schedule_prioritizes_high_priority(self):
        """Verify high priority tasks come before low priority."""
        owner = Owner(name="Jordan", available_time_minutes=60)
        pet = Pet(name="Mochi", species="dog")

        pet.add_task(Task(title="Low task", duration_minutes=10, priority="low", category="grooming"))
        pet.add_task(Task(title="High task", duration_minutes=10, priority="high", category="meds"))

        owner.add_pet(pet)

        scheduler = Scheduler(owner)
        schedule = scheduler.generate_schedule()

        # High priority should come first
        assert schedule[0].title == "High task"
        assert schedule[1].title == "Low task"

    def test_get_total_time(self):
        """Verify total time calculation."""
        owner = Owner(name="Jordan")
        scheduler = Scheduler(owner)

        tasks = [
            Task(title="Task1", duration_minutes=10, priority="high", category="walk"),
            Task(title="Task2", duration_minutes=20, priority="high", category="walk"),
            Task(title="Task3", duration_minutes=15, priority="high", category="walk"),
        ]

        assert scheduler.get_total_time(tasks) == 45


class TestJSONPersistence:
    """Tests for JSON serialization and persistence."""

    def test_task_to_dict_and_back(self):
        """Verify Task can be serialized and deserialized."""
        task = Task(
            title="Walk",
            duration_minutes=30,
            priority="high",
            category="walk",
            pet_name="Mochi",
            completed=True
        )

        task_dict = task.to_dict()
        restored = Task.from_dict(task_dict)

        assert restored.title == task.title
        assert restored.duration_minutes == task.duration_minutes
        assert restored.priority == task.priority
        assert restored.completed == task.completed

    def test_pet_to_dict_and_back(self):
        """Verify Pet with tasks can be serialized and deserialized."""
        pet = Pet(name="Mochi", species="dog")
        pet.add_task(Task(title="Walk", duration_minutes=30, priority="high", category="walk"))
        pet.add_task(Task(title="Feed", duration_minutes=10, priority="medium", category="feeding"))

        pet_dict = pet.to_dict()
        restored = Pet.from_dict(pet_dict)

        assert restored.name == pet.name
        assert restored.species == pet.species
        assert len(restored.tasks) == 2

    def test_owner_to_dict_and_back(self):
        """Verify Owner with pets and tasks can be serialized and deserialized."""
        owner = Owner(name="Jordan", available_time_minutes=90)
        pet = Pet(name="Mochi", species="dog")
        pet.add_task(Task(title="Walk", duration_minutes=30, priority="high", category="walk"))
        owner.add_pet(pet)

        owner_dict = owner.to_dict()
        restored = Owner.from_dict(owner_dict)

        assert restored.name == owner.name
        assert restored.available_time_minutes == 90
        assert len(restored.pets) == 1
        assert len(restored.pets[0].tasks) == 1

    def test_save_and_load_json(self, tmp_path):
        """Verify Owner can be saved to and loaded from JSON file."""
        filepath = tmp_path / "test_data.json"

        owner = Owner(name="Jordan", available_time_minutes=60)
        pet = Pet(name="Mochi", species="dog")
        pet.add_task(Task(title="Walk", duration_minutes=30, priority="high", category="walk"))
        owner.add_pet(pet)

        owner.save_to_json(str(filepath))
        loaded = Owner.load_from_json(str(filepath))

        assert loaded is not None
        assert loaded.name == "Jordan"
        assert len(loaded.pets) == 1
        assert loaded.pets[0].name == "Mochi"

    def test_load_nonexistent_file_returns_none(self):
        """Verify loading from nonexistent file returns None."""
        result = Owner.load_from_json("nonexistent_file_12345.json")
        assert result is None


class TestEmojiHelpers:
    """Tests for emoji helper methods."""

    def test_task_priority_emoji(self):
        """Verify correct priority emojis are returned."""
        high = Task(title="T", duration_minutes=1, priority="high", category="walk")
        medium = Task(title="T", duration_minutes=1, priority="medium", category="walk")
        low = Task(title="T", duration_minutes=1, priority="low", category="walk")

        assert high.get_priority_emoji() == "🔴"
        assert medium.get_priority_emoji() == "🟡"
        assert low.get_priority_emoji() == "🟢"

    def test_task_category_emoji(self):
        """Verify correct category emojis are returned."""
        walk = Task(title="T", duration_minutes=1, priority="high", category="walk")
        feed = Task(title="T", duration_minutes=1, priority="high", category="feeding")
        meds = Task(title="T", duration_minutes=1, priority="high", category="meds")

        assert walk.get_category_emoji() == "🚶"
        assert feed.get_category_emoji() == "🍽️"
        assert meds.get_category_emoji() == "💊"

    def test_pet_species_emoji(self):
        """Verify correct species emojis are returned."""
        dog = Pet(name="Rex", species="dog")
        cat = Pet(name="Whiskers", species="cat")
        other = Pet(name="Goldy", species="other")

        assert dog.get_species_emoji() == "🐕"
        assert cat.get_species_emoji() == "🐱"
        assert other.get_species_emoji() == "🐾"
