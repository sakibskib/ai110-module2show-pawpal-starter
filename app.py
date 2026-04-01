import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to **PawPal+**, your pet care planning assistant!

Add your pets, create care tasks, and generate an optimized daily schedule.
"""
)

# Initialize session state for Owner persistence
if "owner" not in st.session_state:
    st.session_state.owner = None

st.divider()

# Owner Setup Section
st.subheader("Owner Setup")

col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
with col2:
    available_time = st.number_input(
        "Available time (minutes)",
        min_value=15,
        max_value=480,
        value=60,
        help="How much time do you have for pet care today?"
    )

if st.button("Create/Update Owner"):
    st.session_state.owner = Owner(name=owner_name, available_time_minutes=available_time)
    st.success(f"Owner '{owner_name}' created with {available_time} minutes available!")

# Only show pet/task sections if owner exists
if st.session_state.owner:
    owner = st.session_state.owner

    st.divider()

    # Pet Management Section
    st.subheader("Manage Pets")

    col1, col2 = st.columns(2)
    with col1:
        pet_name = st.text_input("Pet name", value="Mochi")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "other"])

    if st.button("Add Pet"):
        # Check if pet already exists
        existing_names = [p.name for p in owner.get_pets()]
        if pet_name in existing_names:
            st.warning(f"Pet '{pet_name}' already exists!")
        else:
            new_pet = Pet(name=pet_name, species=species)
            owner.add_pet(new_pet)
            st.success(f"Added {pet_name} the {species}!")

    # Display existing pets
    if owner.get_pets():
        st.write("**Your Pets:**")
        for pet in owner.get_pets():
            task_count = len(pet.get_tasks())
            st.write(f"- {pet.name} ({pet.species}) - {task_count} task(s)")
    else:
        st.info("No pets yet. Add one above!")

    st.divider()

    # Task Management Section
    st.subheader("Add Tasks")

    if owner.get_pets():
        col1, col2 = st.columns(2)
        with col1:
            selected_pet = st.selectbox(
                "Select pet",
                options=[p.name for p in owner.get_pets()]
            )
        with col2:
            category = st.selectbox(
                "Category",
                ["walk", "feeding", "meds", "grooming", "enrichment"]
            )

        col3, col4, col5 = st.columns(3)
        with col3:
            task_title = st.text_input("Task title", value="Morning walk")
        with col4:
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        with col5:
            priority = st.selectbox("Priority", ["high", "medium", "low"], index=0)

        if st.button("Add Task"):
            # Find the selected pet
            pet = next((p for p in owner.get_pets() if p.name == selected_pet), None)
            if pet:
                new_task = Task(
                    title=task_title,
                    duration_minutes=int(duration),
                    priority=priority,
                    category=category
                )
                pet.add_task(new_task)
                st.success(f"Added '{task_title}' for {selected_pet}!")

        # Display all tasks
        all_tasks = owner.get_all_tasks()
        if all_tasks:
            st.write("**All Tasks:**")
            task_data = [
                {
                    "Pet": t.pet_name,
                    "Task": t.title,
                    "Duration": f"{t.duration_minutes} min",
                    "Priority": t.priority,
                    "Category": t.category,
                    "Done": "Yes" if t.completed else "No"
                }
                for t in all_tasks
            ]
            st.table(task_data)
        else:
            st.info("No tasks yet. Add some above!")
    else:
        st.info("Add a pet first before creating tasks.")

    st.divider()

    # Schedule Generation Section
    st.subheader("Generate Daily Schedule")
    st.caption(f"Available time: {owner.available_time_minutes} minutes")

    if st.button("Generate Schedule"):
        scheduler = Scheduler(owner)
        schedule = scheduler.generate_schedule()

        if schedule:
            st.success("Schedule generated!")

            # Display schedule as a nice table
            schedule_data = []
            for i, task in enumerate(schedule, 1):
                schedule_data.append({
                    "Order": i,
                    "Task": task.title,
                    "Pet": task.pet_name,
                    "Duration": f"{task.duration_minutes} min",
                    "Priority": task.priority
                })
            st.table(schedule_data)

            # Show time summary
            total_time = scheduler.get_total_time(schedule)
            st.metric(
                "Time Used",
                f"{total_time} / {owner.available_time_minutes} min",
                delta=f"{owner.available_time_minutes - total_time} min remaining"
            )

            # Show explanation
            with st.expander("Why this schedule?"):
                explanation = scheduler.explain_schedule(schedule)
                st.code(explanation, language=None)
        else:
            st.warning("No tasks to schedule! Add some tasks first.")

    # Mark tasks complete section
    all_tasks = owner.get_all_tasks()
    incomplete_tasks = [t for t in all_tasks if not t.completed]

    if incomplete_tasks:
        st.divider()
        st.subheader("Mark Tasks Complete")

        task_options = [f"{t.title} ({t.pet_name})" for t in incomplete_tasks]
        selected_task_str = st.selectbox("Select task to complete", task_options)

        if st.button("Mark Complete"):
            idx = task_options.index(selected_task_str)
            incomplete_tasks[idx].mark_complete()
            st.success(f"Marked '{incomplete_tasks[idx].title}' as complete!")
            st.rerun()

else:
    st.info("Create an owner above to get started!")
