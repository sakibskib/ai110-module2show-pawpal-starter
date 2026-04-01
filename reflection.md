# PawPal+ Project Reflection

## 1. System Design

### Core User Actions

1. **Register Pet & Owner** - The user can add their pet's information (name, species) along with owner details (name, daily available time for pet care). This establishes the foundation for task planning.

2. **Add/Edit Care Tasks** - The user can create and manage pet care tasks such as walks, feeding, medications, grooming, and enrichment activities. Each task includes a title, duration in minutes, priority level (low/medium/high), and category.

3. **Generate Daily Schedule** - The user can generate an optimized daily schedule that arranges tasks based on available time and priority. The system explains why it chose the order and which tasks fit within the time constraints.

---

**a. Initial design**

My initial UML design includes four core classes:

1. **Task (dataclass)**: Represents a pet care task with attributes for title, duration, priority, category, and completion status. Uses a simple `mark_complete()` method to track progress.

2. **Pet (dataclass)**: Represents a pet with name and species. Holds a list of Tasks and provides methods to add/retrieve tasks. This keeps task management pet-specific.

3. **Owner (dataclass)**: Represents the pet owner with name and available time. Holds a list of Pets and provides methods to add/retrieve pets. The available_time_minutes attribute is key for scheduling constraints.

4. **Scheduler**: The "brain" of the system. Takes an Owner and orchestrates schedule generation. Responsible for:
   - Gathering all tasks from all pets
   - Sorting/filtering by priority and time constraints
   - Generating an optimized schedule
   - Explaining why tasks were chosen and ordered

**b. Design changes**

After reviewing the skeleton with AI, I identified these potential improvements:

1. **Added helper method to Scheduler**: The `all_tasks` list should be populated automatically by collecting tasks from all pets. Added a `_collect_all_tasks()` private method to gather tasks from all pets owned by the owner.

2. **Task-Pet relationship**: Considered adding a `pet_name` attribute to Task so explanations can say "Walk for Mochi" instead of just "Walk". This improves the user experience when explaining the schedule.

3. **Priority constant**: Could use an Enum for priority levels instead of strings to prevent typos, but kept strings for simplicity since the UI uses string dropdowns.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
