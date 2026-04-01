# PawPal+ UML Class Diagram

```mermaid
classDiagram
    class Owner {
        +str name
        +int available_time_minutes
        +list~Pet~ pets
        +add_pet(pet: Pet) void
        +get_pets() list~Pet~
    }

    class Pet {
        +str name
        +str species
        +list~Task~ tasks
        +add_task(task: Task) void
        +get_tasks() list~Task~
    }

    class Task {
        +str title
        +int duration_minutes
        +str priority
        +str category
        +str pet_name
        +bool completed
        +mark_complete() void
    }

    class Scheduler {
        +Owner owner
        +list~Task~ all_tasks
        -_collect_all_tasks() list~Task~
        +generate_schedule() list~Task~
        +explain_schedule(schedule: list~Task~) str
        +get_total_time(tasks: list~Task~) int
    }

    Owner "1" --> "*" Pet : has
    Pet "1" --> "*" Task : has
    Scheduler "1" --> "1" Owner : manages
    Scheduler "1" --> "*" Task : schedules
```

## Relationships

- **Owner has Pets**: One owner can have multiple pets (1 to many)
- **Pet has Tasks**: Each pet can have multiple care tasks (1 to many)
- **Scheduler manages Owner**: The scheduler works with one owner's data
- **Scheduler schedules Tasks**: The scheduler organizes all tasks into a daily plan
