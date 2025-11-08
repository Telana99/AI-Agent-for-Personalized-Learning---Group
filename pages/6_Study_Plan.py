import streamlit as st
from modules import db, helpers

helpers.set_page_styling()

st.set_page_config(page_title="Study Plan", page_icon="📅", layout="centered")

# Check if user is logged in
if 'user_id' not in st.session_state or 'selected_subject' not in st.session_state:
    st.page_link("pages/0_Login.py", label="Go to Login", icon="🔑")
    st.stop()

subject = st.session_state['selected_subject']
user_id = st.session_state['user_id']

st.title(f"📅 Create Your {subject} Study Plan")
st.write("Let's create a personalized study plan based on your available time!")

# Get existing study hours from database
existing_hours = db.get_study_hours(user_id, subject)

# Simple form to collect hours
with st.form("study_plan_form"):
    st.subheader("How much time can you dedicate?")
    
    hours_per_day = st.number_input(
        "Hours per day:",
        min_value=0.5,
        max_value=12.0,
        value=existing_hours if existing_hours else 1.0,  # Show saved hours if they exist
        step=0.5,
        help="How many hours per day can you study?"
    )
    
    submitted = st.form_submit_button("Create My Study Plan")
    
    if submitted:
        # Save to DATABASE now!
        db.update_study_hours(user_id, subject, hours_per_day)
        st.success(f"✅ Great! You'll study {hours_per_day} hours per day.")
        st.success("💾 Your study plan has been saved!")
        st.balloons()

# Show current plan if it exists
saved_hours = db.get_study_hours(user_id, subject)
if saved_hours:
    st.markdown("---")
    st.info(f"📊 Your current plan: **{saved_hours} hours/day**")
    st.caption("You can update this anytime by entering new hours above.")