import streamlit as st
from pawpal_system import (
    Owner, Pet, Task, Scheduler,
    PRIORITY_EMOJI, CATEGORY_EMOJI, SPECIES_EMOJI
)

DATA_FILE = "data.json"

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to **PawPal+**, your pet care planning assistant!

Add your pets, create care tasks, and generate an optimized daily schedule.
Your data is automatically saved and will persist between sessions.
"""
)

# Initialize session state - try to load from JSON first
if "owner" not in st.session_state:
    loaded_owner = Owner.load_from_json(DATA_FILE)
    st.session_state.owner = loaded_owner


def save_data():
    """Save current owner data to JSON."""
    if st.session_state.owner:
        st.session_state.owner.save_to_json(DATA_FILE)


st.divider()

# Owner Setup Section
st.subheader("👤 Owner Setup")

col1, col2 = st.columns(2)
with col1:
    default_name = st.session_state.owner.name if st.session_state.owner else "Jordan"
    owner_name = st.text_input("Owner name", value=default_name)
with col2:
    default_time = st.session_state.owner.available_time_minutes if st.session_state.owner else 60
    available_time = st.number_input(
        "Available time (minutes)",
        min_value=15,
        max_value=480,
        value=default_time,
        help="How much time do you have for pet care today?"
    )

col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    if st.button("Create/Update Owner", type="primary"):
        if st.session_state.owner:
            # Update existing owner
            st.session_state.owner.name = owner_name
            st.session_state.owner.available_time_minutes = available_time
        else:
            st.session_state.owner = Owner(name=owner_name, available_time_minutes=available_time)
        save_data()
        st.success(f"Owner '{owner_name}' saved with {available_time} minutes available!")

with col_btn2:
    if st.session_state.owner and st.button("Clear All Data", type="secondary"):
        st.session_state.owner = None
        import os
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        st.rerun()

# Only show pet/task sections if owner exists
if st.session_state.owner:
    owner = st.session_state.owner

    st.divider()

    # Pet Management Section
    st.subheader("🐾 Manage Pets")

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
            save_data()
            st.success(f"Added {SPECIES_EMOJI.get(species, '🐾')} {pet_name} the {species}!")
            st.rerun()

    # Display existing pets with emojis
    if owner.get_pets():
        st.write("**Your Pets:**")
        for pet in owner.get_pets():
            task_count = len(pet.get_tasks())
            incomplete = len(pet.get_incomplete_tasks())
            emoji = pet.get_species_emoji()
            st.write(f"- {emoji} **{pet.name}** ({pet.species}) - {task_count} task(s), {incomplete} pending")
    else:
        st.info("No pets yet. Add one above!")

    st.divider()

    # Task Management Section
    st.subheader("📋 Add Tasks")

    if owner.get_pets():
        col1, col2 = st.columns(2)
        with col1:
            pet_options = [f"{p.get_species_emoji()} {p.name}" for p in owner.get_pets()]
            selected_pet_display = st.selectbox("Select pet", options=pet_options)
            selected_pet = owner.get_pets()[pet_options.index(selected_pet_display)].name
        with col2:
            category_options = ["walk", "feeding", "meds", "grooming", "enrichment"]
            category_display = [f"{CATEGORY_EMOJI.get(c, '📋')} {c}" for c in category_options]
            selected_category_display = st.selectbox("Category", category_display)
            category = category_options[category_display.index(selected_category_display)]

        col3, col4, col5 = st.columns(3)
        with col3:
            task_title = st.text_input("Task title", value="Morning walk")
        with col4:
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        with col5:
            priority_options = ["high", "medium", "low"]
            priority_display = [f"{PRIORITY_EMOJI.get(p, '⚪')} {p}" for p in priority_options]
            selected_priority_display = st.selectbox("Priority", priority_display, index=0)
            priority = priority_options[priority_display.index(selected_priority_display)]

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
                save_data()
                st.success(f"Added '{task_title}' for {selected_pet}!")
                st.rerun()

        # Display all tasks with emojis
        all_tasks = owner.get_all_tasks()
        if all_tasks:
            st.write("**All Tasks:**")
            task_data = [
                {
                    "Priority": f"{t.get_priority_emoji()}",
                    "Category": f"{t.get_category_emoji()}",
                    "Pet": t.pet_name,
                    "Task": t.title,
                    "Duration": f"{t.duration_minutes} min",
                    "Status": "✅ Done" if t.completed else "⏳ Pending"
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
    st.subheader("📅 Generate Daily Schedule")
    st.caption(f"⏱️ Available time: **{owner.available_time_minutes} minutes**")

    if st.button("Generate Schedule", type="primary"):
        scheduler = Scheduler(owner)
        schedule = scheduler.generate_schedule()

        if schedule:
            st.success("✨ Schedule generated!")

            # Display schedule as a nice table with emojis
            schedule_data = []
            for i, task in enumerate(schedule, 1):
                schedule_data.append({
                    "#": i,
                    "Priority": task.get_priority_emoji(),
                    "Type": task.get_category_emoji(),
                    "Task": task.title,
                    "Pet": task.pet_name,
                    "Duration": f"{task.duration_minutes} min"
                })
            st.table(schedule_data)

            # Show time summary with visual progress
            total_time = scheduler.get_total_time(schedule)
            remaining = owner.available_time_minutes - total_time
            progress = total_time / owner.available_time_minutes

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Time Used", f"{total_time} min", delta=None)
            with col2:
                st.metric("Time Remaining", f"{remaining} min", delta=None)

            st.progress(progress, text=f"{int(progress * 100)}% of available time scheduled")

            # Show explanation
            with st.expander("📖 Why this schedule?"):
                explanation = scheduler.explain_schedule(schedule)
                st.code(explanation, language=None)
        else:
            st.warning("No tasks to schedule! Add some tasks first.")

    # Mark tasks complete section
    all_tasks = owner.get_all_tasks()
    incomplete_tasks = [t for t in all_tasks if not t.completed]

    if incomplete_tasks:
        st.divider()
        st.subheader("✅ Mark Tasks Complete")

        task_options = [
            f"{t.get_priority_emoji()} {t.get_category_emoji()} {t.title} ({t.pet_name})"
            for t in incomplete_tasks
        ]
        selected_task_str = st.selectbox("Select task to complete", task_options)

        if st.button("Mark Complete"):
            idx = task_options.index(selected_task_str)
            incomplete_tasks[idx].mark_complete()
            save_data()
            st.success(f"✅ Marked '{incomplete_tasks[idx].title}' as complete!")
            st.rerun()

else:
    st.info("👆 Create an owner above to get started!")

# Footer
st.divider()
st.caption("💾 Data is automatically saved to `data.json`")
