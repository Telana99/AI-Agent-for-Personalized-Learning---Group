import streamlit as st
from modules import db, helpers
import json
from datetime import datetime, timedelta

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

try:
    with open(f"curriculum/{subject.lower()}_curriculum.json") as f:
        curriculum = json.load(f)['full_path']
except FileNotFoundError:
    st.error(f"Curriculum for {subject} not found.")
    st.stop()

progress = db.get_or_create_progress(user_id, subject)
current_topic_index = progress['topic_index']
total_topics = len(curriculum)
remaining_topics = total_topics - current_topic_index

existing_hours = db.get_study_hours(user_id, subject)

with st.form("study_plan_form"):
    st.subheader("How much time can you dedicate?")
    
    hours_per_day = st.number_input(
        "Hours per day:",
        min_value=0.5,
        max_value=12.0,
        value=existing_hours if existing_hours else 1.0,
        step=0.5,
        help="How many hours per day can you study?"
    )
    
    submitted = st.form_submit_button("Create My Study Plan")
    
    if submitted:
        db.update_study_hours(user_id, subject, hours_per_day)
        st.success(f"✅ Great! You'll study {hours_per_day} hours per day.")
        st.success("💾 Your study plan has been saved!")

saved_hours = db.get_study_hours(user_id, subject)
if saved_hours:
    st.markdown("---")
    st.subheader("📊 Your Study Plan Summary")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Study Time", f"{saved_hours} hrs/day")
    with col2:
        st.metric("Topics Left", remaining_topics)
    with col3:
        st.metric("Total Topics", total_topics)
    

    user_level = progress['level']  
    
    if user_level == 'beginner':
        hours_per_topic = 1.5  
    elif user_level == 'intermediate':
        hours_per_topic = 1.0 
    elif user_level == 'advanced':
        hours_per_topic = 0.5 
    else:
        hours_per_topic = 1.0  
    

    beginner_topics = 0
    intermediate_topics = 0
    advanced_topics = 0
    
    for i in range(current_topic_index, total_topics):
        topic_level = curriculum[i]['level']
        if topic_level == 'beginner':
            beginner_topics += 1
        elif topic_level == 'intermediate':
            intermediate_topics += 1
        elif topic_level == 'advanced':
            advanced_topics += 1
    
    if user_level == 'beginner':
        total_hours_needed = (beginner_topics * 1.0) + (intermediate_topics * 1.5) + (advanced_topics * 2.0)
    elif user_level == 'intermediate':
        total_hours_needed = (beginner_topics * 0.5) + (intermediate_topics * 1.0) + (advanced_topics * 1.5)
    elif user_level == 'advanced':
        total_hours_needed = (beginner_topics * 0.3) + (intermediate_topics * 0.5) + (advanced_topics * 1.0)
    else:
        total_hours_needed = remaining_topics * 1.0

    days_needed = total_hours_needed / saved_hours
    
    import math
    days_needed = math.ceil(days_needed)
    
    today = datetime.now()
    completion_date = today + timedelta(days=days_needed)
    
    st.markdown("---")
    st.subheader("🎯 Estimated Completion")
    if user_level:
        if user_level == 'beginner':
            st.info("🎓 **Personalized for Beginners:** We've allocated extra time for challenging topics!")
        elif user_level == 'intermediate':
            st.info("⚡ **Personalized for Intermediate:** Balanced pace based on your skill level!")
        elif user_level == 'advanced':
            st.info("🚀 **Personalized for Advanced:** Faster track - you'll breeze through basics!")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Total Hours Needed:** {total_hours_needed} hours")
        st.info(f"**Days to Complete:** {days_needed} days")
    with col2:
        st.success(f"**Target Date:** {completion_date.strftime('%B %d, %Y')}")
        st.caption(f"Starting from today: {today.strftime('%B %d, %Y')}")
    
    # Show breakdown
    with st.expander("📋 See personalized calculation details"):
        st.write(f"**Your Skill Level:** {user_level.capitalize() if user_level else 'Not set'}")
        st.write("")
        st.write("**Remaining Topics Breakdown:**")
        st.write(f"- 🟢 Beginner topics: **{beginner_topics}**")
        st.write(f"- 🟡 Intermediate topics: **{intermediate_topics}**")
        st.write(f"- 🔴 Advanced topics: **{advanced_topics}**")
        st.write("")
        st.write("**Time Estimates (personalized for you):**")
        
        if user_level == 'beginner':
            st.write(f"- 🟢 Beginner topics: {beginner_topics} × 1.0 hrs = **{beginner_topics * 1.0} hrs**")
            st.write(f"- 🟡 Intermediate topics: {intermediate_topics} × 1.5 hrs = **{intermediate_topics * 1.5} hrs**")
            st.write(f"- 🔴 Advanced topics: {advanced_topics} × 2.0 hrs = **{advanced_topics * 2.0} hrs**")
        elif user_level == 'intermediate':
            st.write(f"- 🟢 Beginner topics: {beginner_topics} × 0.5 hrs = **{beginner_topics * 0.5} hrs**")
            st.write(f"- 🟡 Intermediate topics: {intermediate_topics} × 1.0 hrs = **{intermediate_topics * 1.0} hrs**")
            st.write(f"- 🔴 Advanced topics: {advanced_topics} × 1.5 hrs = **{advanced_topics * 1.5} hrs**")
        elif user_level == 'advanced':
            st.write(f"- 🟢 Beginner topics: {beginner_topics} × 0.3 hrs = **{beginner_topics * 0.3} hrs**")
            st.write(f"- 🟡 Intermediate topics: {intermediate_topics} × 0.5 hrs = **{intermediate_topics * 0.5} hrs**")
            st.write(f"- 🔴 Advanced topics: {advanced_topics} × 1.0 hrs = **{advanced_topics * 1.0} hrs**")
        
        st.write("")
        st.write(f"**Total time needed:** {total_hours_needed} hours")
        st.write(f"**You study:** {saved_hours} hours/day")
        st.write(f"**Days needed:** {total_hours_needed} ÷ {saved_hours} = **{days_needed} days**")
        
        st.caption("💡 This is personalized based on YOUR skill level and the difficulty of remaining topics!")
    
    st.caption("💡 You can update your daily hours anytime above to see a new estimate!")

    st.markdown("---")
    st.subheader("📆 Your Daily Study Schedule")
    st.write("Here's what you should study each day:")
    
    daily_schedule = []
    current_day = 1
    hours_accumulated = 0
    topics_for_today = []
    
    for i in range(current_topic_index, total_topics):
        topic_name = curriculum[i]['topic']
        topic_level = curriculum[i]['level']
        
        if user_level == 'beginner':
            if topic_level == 'beginner':
                topic_hours = 1.0
            elif topic_level == 'intermediate':
                topic_hours = 1.5
            else: 
                topic_hours = 2.0
        elif user_level == 'intermediate':
            if topic_level == 'beginner':
                topic_hours = 0.5
            elif topic_level == 'intermediate':
                topic_hours = 1.0
            else: 
                topic_hours = 1.5
        elif user_level == 'advanced':
            if topic_level == 'beginner':
                topic_hours = 0.3
            elif topic_level == 'intermediate':
                topic_hours = 0.5
            else: 
                topic_hours = 1.0
        else:
            topic_hours = 1.0 
        
        if hours_accumulated + topic_hours <= saved_hours:
            topics_for_today.append({
                'topic': topic_name,
                'level': topic_level,
                'hours': topic_hours
            })
            hours_accumulated += topic_hours
        else:
            if topics_for_today:
                daily_schedule.append({
                    'day': current_day,
                    'topics': topics_for_today.copy(),
                    'total_hours': hours_accumulated
                })
            
            current_day += 1
            topics_for_today = [{
                'topic': topic_name,
                'level': topic_level,
                'hours': topic_hours
            }]
            hours_accumulated = topic_hours
    
    if topics_for_today:
        daily_schedule.append({
            'day': current_day,
            'topics': topics_for_today.copy(),
            'total_hours': hours_accumulated
        })
    
    if daily_schedule:
        days_to_show = min(7, len(daily_schedule))
        
        st.info(f"📅 Showing your first **{days_to_show} days** of study (out of {len(daily_schedule)} total days)")
        
        for day_data in daily_schedule[:days_to_show]:
            day_num = day_data['day']
            day_date = (datetime.now() + timedelta(days=day_num-1)).strftime('%b %d, %Y')
            
            with st.expander(f"📅 **Day {day_num}** ({day_date}) - {day_data['total_hours']:.1f} hours", expanded=(day_num==1)):
                for topic_info in day_data['topics']:
                    if topic_info['level'] == 'beginner':
                        badge = "🟢"
                    elif topic_info['level'] == 'intermediate':
                        badge = "🟡"
                    else:
                        badge = "🔴"
                    
                    st.markdown(f"{badge} **{topic_info['topic']}** - *{topic_info['hours']} hrs* ({topic_info['level']})")
                
                st.caption(f"Total: {day_data['total_hours']:.1f} hours")
        
        if len(daily_schedule) > 7:
            st.caption(f"... and {len(daily_schedule) - 7} more days. Keep going! 💪")
        
        st.markdown("---")
        st.success(f"✅ **Complete all {len(daily_schedule)} days to finish your {subject} course!**")
    else:
        st.warning("No topics remaining! You've completed the course! 🎉")