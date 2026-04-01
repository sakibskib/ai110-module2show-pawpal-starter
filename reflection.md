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

My scheduler considers two main constraints:

1. **Time constraint**: The owner specifies how many minutes they have available for pet care. The scheduler won't exceed this limit, even if there are more tasks to complete. This felt like the most practical constraint because busy pet owners genuinely have limited time.

2. **Priority levels**: Tasks are sorted by priority (high → medium → low) first, then by duration (shorter tasks first within the same priority). I decided priority should matter most because a medication dose is objectively more important than brushing fur, regardless of how long each takes.

I chose this ordering because in real life, if I only had 30 minutes, I'd want to make sure my pet gets their medicine before I worry about playtime. The scheduler reflects that common-sense thinking.

**b. Tradeoffs**

One key tradeoff is that my scheduler uses a **greedy algorithm** - it picks the highest priority task that fits the remaining time and moves on. This means it might skip a high-priority 45-minute task in favor of three 15-minute medium-priority tasks if time is tight.

This tradeoff is reasonable for daily pet care because:
- Most pet care tasks are relatively short (5-30 minutes)
- Missing one task today isn't catastrophic - you can reschedule for tomorrow
- The greedy approach is simple to understand and explain to users

A more sophisticated algorithm (like knapsack optimization) could theoretically pack tasks more efficiently, but it would be harder to explain why certain choices were made, and the marginal improvement wouldn't justify the complexity for this use case.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI tools throughout every phase of this project:

- **Design brainstorming**: I described the pet care scenario and asked for help identifying the core classes and their relationships. The AI helped me think through what attributes each class needed and how they should connect.

- **Code generation**: For the class skeletons and the Mermaid UML diagram, I provided the conceptual design and let the AI generate the boilerplate. This saved time on repetitive typing.

- **Debugging and integration**: When connecting the backend to Streamlit, I asked the AI how `st.session_state` works and how to persist objects across page refreshes. This was way faster than reading through documentation.

The most helpful prompts were specific and contextual, like: "Based on my class skeletons, how should the Scheduler retrieve all tasks from the Owner's pets?" Vague questions got vague answers, but pointed questions got exactly what I needed.

**b. Judgment and verification**

One moment I didn't accept an AI suggestion as-is was when it initially suggested using Enums for priority levels. The suggestion made sense from a type-safety perspective, but I realized the Streamlit dropdown returns strings like "high" and "medium". Adding Enum conversion would mean extra code to translate between string inputs and Enum values.

I evaluated this by thinking through the actual user flow: user selects "high" from dropdown → that value needs to work directly with my Task class. Keeping priorities as strings meant less friction and fewer places for bugs to hide. Sometimes the "cleaner" solution isn't the practical one.

I also verified the scheduling algorithm by running the CLI demo with different task combinations. When I saw "Give medication" consistently appearing before "Morning walk" (both high priority, but medication is shorter), I knew the sorting logic was working as intended.

---

## 4. Testing and Verification

**a. What you tested**

I wrote 10 pytest tests covering the most critical behaviors:

1. **Task completion**: Verifying that `mark_complete()` actually changes `task.completed` from False to True. This is fundamental - if marking tasks done doesn't work, the whole app breaks.

2. **Task addition**: Checking that adding a task to a Pet increases the task count and that the `pet_name` gets set automatically. This ensures tasks are properly associated with their pets.

3. **Scheduler constraints**: Testing that the generated schedule never exceeds the owner's available time, and that high-priority tasks come before low-priority ones.

These tests are important because they catch regressions. If I later refactor the Scheduler and accidentally break priority sorting, the test will fail immediately instead of me discovering the bug after deploying.

**b. Confidence**

I'm fairly confident the scheduler works correctly for typical use cases. The CLI demo showed sensible output with multiple pets and varied task priorities. The tests pass consistently.

Edge cases I'd test next with more time:
- What happens when available time is 0 minutes?
- What if all tasks are larger than the available time (nothing should be scheduled)?
- Tasks with identical priority AND duration - is the order deterministic?
- Very large numbers of tasks (100+) - does performance hold up?

---

## 5. Reflection

**a. What went well**

I'm most satisfied with how the scheduling logic turned out. The `generate_schedule()` method is only about 15 lines of code, but it handles the core algorithm cleanly: collect tasks, sort by priority and duration, greedily select what fits. The `explain_schedule()` method then makes it transparent to users why certain tasks were chosen.

The CLI-first workflow was also a win. Testing in `main.py` before touching Streamlit meant I could debug the logic in isolation. When I finally integrated with the UI, it worked on the first try because I knew the backend was solid.

**b. What you would improve**

If I had another iteration, I'd add:

1. **Task recurrence**: Right now all tasks are one-time. I'd want to support "feed breakfast every day" or "vet appointment next Tuesday."

2. **Better time slot awareness**: The current scheduler doesn't know that walks should happen in the morning. Adding preferred time windows would make schedules more realistic.

3. **Data persistence**: Currently everything resets when you close the browser. Saving to JSON or a database would make the app actually usable day-to-day.

**c. Key takeaway**

The biggest lesson was that **I'm the architect, not the AI**. The AI is incredibly fast at generating code and suggesting patterns, but it doesn't know my specific constraints - like how Streamlit handles state, or that I want priority to matter more than duration.

When I gave clear, specific instructions and reviewed the output critically, AI made me faster. When I accepted suggestions blindly, I ended up with code that technically worked but didn't fit my design. The skill isn't just knowing how to prompt - it's knowing when to say "no, that's not what I need" and steering the collaboration back on track.

Being the "lead architect" means owning the decisions, even when the AI wrote 80% of the code. I still had to understand every line, justify every tradeoff, and take responsibility for the final product.
