"""
PawPal+ Demo Script

This script demonstrates the core functionality of the PawPal+ system.
Run with: python main.py
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def main():
    print("=" * 60)
    print("       PawPal+ Demo - Pet Care Scheduling System")
    print("=" * 60)
    print()

    # Create an owner with 60 minutes available
    owner = Owner(name="Jordan", available_time_minutes=60)
    print(f"Owner: {owner.name}")
    print(f"Available time: {owner.available_time_minutes} minutes")
    print()

    # Create two pets
    mochi = Pet(name="Mochi", species="dog")
    whiskers = Pet(name="Whiskers", species="cat")

    owner.add_pet(mochi)
    owner.add_pet(whiskers)

    print(f"Pets: {', '.join(pet.name for pet in owner.get_pets())}")
    print()

    # Add tasks for Mochi (dog)
    mochi.add_task(Task(
        title="Morning walk",
        duration_minutes=30,
        priority="high",
        category="walk"
    ))
    mochi.add_task(Task(
        title="Brush fur",
        duration_minutes=15,
        priority="low",
        category="grooming"
    ))
    mochi.add_task(Task(
        title="Give medication",
        duration_minutes=5,
        priority="high",
        category="meds"
    ))

    # Add tasks for Whiskers (cat)
    whiskers.add_task(Task(
        title="Feed breakfast",
        duration_minutes=10,
        priority="high",
        category="feeding"
    ))
    whiskers.add_task(Task(
        title="Play with feather toy",
        duration_minutes=20,
        priority="medium",
        category="enrichment"
    ))
    whiskers.add_task(Task(
        title="Clean litter box",
        duration_minutes=10,
        priority="medium",
        category="grooming"
    ))

    # Display all tasks
    print("All Tasks:")
    print("-" * 40)
    for pet in owner.get_pets():
        print(f"\n{pet.name} ({pet.species}):")
        for task in pet.get_tasks():
            print(f"  {task}")

    print()
    print("=" * 60)
    print("                  TODAY'S SCHEDULE")
    print("=" * 60)
    print()

    # Generate and display schedule
    scheduler = Scheduler(owner)
    schedule = scheduler.generate_schedule()

    explanation = scheduler.explain_schedule(schedule)
    print(explanation)

    print()
    print("=" * 60)

    # Demo: Mark a task complete and regenerate
    print("\n[Demo] Marking 'Morning walk' as complete...")
    mochi.get_tasks()[0].mark_complete()

    print("\nRegenerated schedule after completing a task:")
    print("-" * 50)
    schedule = scheduler.generate_schedule()
    explanation = scheduler.explain_schedule(schedule)
    print(explanation)


if __name__ == "__main__":
    main()
