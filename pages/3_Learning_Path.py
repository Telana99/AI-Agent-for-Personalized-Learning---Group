import streamlit as st
from modules import llm, db, helpers
import json

helpers.set_page_styling()

st.set_page_config(page_title="Learning Path", page_icon="📚", layout="wide")
if 'user_id' not in st.session_state or 'selected_subject' not in st.session_state:
    st.page_link("pages/0_Login.py", label="Go to Login", icon="🔑")
    st.stop()

subject = st.session_state['selected_subject']

try:
    with open(f"curriculum/{subject.lower()}_curriculum.json") as f:
        curriculum = json.load(f)['full_path']
except FileNotFoundError:
    st.error(f"Curriculum for {subject} not found.")
    st.stop()

topics = [item['topic'] for item in curriculum]
progress_data = db.get_or_create_progress(st.session_state['user_id'], subject)
topic_index = progress_data['topic_index']

todays_plan = db.get_todays_study_plan(st.session_state['user_id'], subject)

failed_assignment = progress_data['assignment_score'] is not None and progress_data['status'] == 'learning'
revise_mode_flag = st.session_state.get('revise_mode', False)
review_mode = failed_assignment or revise_mode_flag

if review_mode:
    if revise_mode_flag:
        st.info("📖 You are in **Revise Mode**. All lessons are unlocked for your review.")
    else:
        st.info("📖 You are in **Review Mode**. Study what you need and retake the assignment when you're ready.")
else:
    st.title(f"🚀 Your {subject.capitalize()} Learning Path")

    if 'viewing_topic_index' not in st.session_state:
        if review_mode:
            st.session_state.viewing_topic_index = 0
        else:
            st.session_state.viewing_topic_index = topic_index
    
    if todays_plan:
        st.success("📅 **Today's Study Plan**")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            topics_completed = todays_plan.get('completed_topics', 0)
            total_topics_in_course = len(topics)
            progress_percentage = (topics_completed / total_topics_in_course * 100) if total_topics_in_course > 0 else 0
            
            #st.write(f"**Day {todays_plan['day']} of {todays_plan['total_days']}** - Study for {todays_plan['total_hours']:.1f} hours today")
            st.progress(progress_percentage / 100, text=f"Course Progress: {topics_completed}/{total_topics_in_course} topics ({progress_percentage:.0f}%)")
            
            topic_names = []
            for topic_info in todays_plan['topics']:
                if topic_info['level'] == 'beginner':
                    badge = "🟢"
                elif topic_info['level'] == 'intermediate':
                    badge = "🟡"
                else:
                    badge = "🔴"
                topic_names.append(f"{badge} {topic_info['topic']}")
            
            st.write("**Today's Topics:** " + " → ".join(topic_names))
        
        with col2:
            if st.button("📊 View Full Plan", use_container_width=True):
                st.switch_page("pages/6_Study_Plan.py")
        
        st.markdown("---")
        # Quick jump to first topic of the day if not already there
        if todays_plan['topics'] and st.session_state.viewing_topic_index not in [t['index'] for t in todays_plan['topics']]:
            first_topic_index = todays_plan['topics'][0]['index']
            first_topic_name = todays_plan['topics'][0]['topic']
            
            if st.button(f"▶️ Jump to Today's First Topic: {first_topic_name}", use_container_width=True):
                st.session_state.viewing_topic_index = first_topic_index
                st.rerun()
    else:
        st.info("💡 **Tip:** Create a study plan to get daily recommendations!")
        if st.button("📅 Create Study Plan"):
            st.switch_page("pages/6_Study_Plan.py")
        st.markdown("---")

if not review_mode and topic_index >= len(topics):
    st.success("🎉 You've completed all the lessons in the learning path!")
    st.markdown("---")
    st.subheader("What would you like to do next?")
    cols = st.columns(2)
    with cols[0]:
        if st.button("Review Lessons", use_container_width=True):
            st.session_state['revise_mode'] = True
            st.rerun()
    with cols[1]:
        if st.button("Take Final Assignment", type="primary", use_container_width=True):
            db.update_progress(st.session_state['user_id'], subject, status='assessing')
            st.switch_page("pages/4_Assignments.py")
    st.stop()
    


st.sidebar.header("Course Outline")

#Get today's recommended topic indices 
todays_topic_indices = []
if todays_plan and not review_mode:
    todays_topic_indices = [t['index'] for t in todays_plan['topics']]

for i, topic_name in enumerate(topics):
    if review_mode:
        btn_type = "primary" if i == st.session_state.viewing_topic_index else "secondary"
        if st.sidebar.button(f"📖 {topic_name}", key=f"topic_{i}", type=btn_type):
            st.session_state.viewing_topic_index = i
            st.rerun()
    else:
        #Mark today's topics with a star 
        is_todays_topic = i in todays_topic_indices
        topic_prefix = "⭐ " if is_todays_topic else ""
        
        if i < topic_index:
            btn_type = "primary" if i == st.session_state.viewing_topic_index else "secondary"
            if st.sidebar.button(f"✅ {topic_prefix}{topic_name}", key=f"topic_{i}", type=btn_type):
                st.session_state.viewing_topic_index = i
                st.rerun()
        elif i == topic_index:
            st.sidebar.button(f"▶️ {topic_prefix}{topic_name}", type="primary", key=f"topic_{i}")
        else:
            st.sidebar.button(f"🔒 {topic_prefix}{topic_name}", disabled=True, key=f"topic_{i}")


if todays_topic_indices and not review_mode:
    st.sidebar.markdown("---")
    st.sidebar.caption("⭐ = Today's recommended topics")

if failed_assignment:
    st.sidebar.markdown("---")
    if st.sidebar.button("Ready to Retake Assignment", type="primary"):
        db.update_progress(st.session_state['user_id'], subject, status='assessing')
        if 'assignment_questions' in st.session_state: del st.session_state.assignment_questions
        st.switch_page("pages/4_Assignments.py")

viewing_index = st.session_state.viewing_topic_index
current_topic = topics[viewing_index]
current_level = curriculum[viewing_index]['level']

st.header(f"Chapter {viewing_index + 1}: {current_topic}")
st.caption(f"Difficulty Level: {current_level.capitalize()}")

#  Show progress against study plan 
if todays_plan and not review_mode:
    viewing_is_todays_topic = viewing_index in [t['index'] for t in todays_plan['topics']]
    
    if viewing_is_todays_topic:
        # Find which number topic this is for today (1st, 2nd, 3rd...)
        topic_position = None
        for idx, t in enumerate(todays_plan['topics']):
            if t['index'] == viewing_index:
                topic_position = idx + 1
                break
        
        if topic_position:
            total_today = len(todays_plan['topics'])
            if total_today == 1:
                st.success("⭐ This is today's recommended topic! You've got this! 💪")
            else:
                st.success(f"⭐ Today's topic {topic_position} of {total_today}! Keep up the momentum! 🚀")
    else:
        if viewing_index < topic_index:
            st.info("✅ You've already completed this topic. Great job! 🎉")
        elif viewing_index > topic_index:
            st.warning("🔒 This topic is locked. Complete earlier topics first to unlock it!")

lesson_key = f"lesson_{viewing_index}"
if lesson_key not in st.session_state:
    with st.spinner("Loading lesson..."):
        prompt = f"Provide a detailed lesson for a '{current_level}' level {subject} student on the topic: '{current_topic}'. Include simple code examples."
        st.session_state[lesson_key] = llm.ask_ai(prompt, language=subject)
st.markdown(st.session_state[lesson_key])

#coding challenge
if not review_mode and viewing_index == topic_index:
    st.subheader("🧑‍💻 Coding Challenge")
    coding_key = f"coding_{viewing_index}"
    if coding_key not in st.session_state:
        challenge_prompt = f"Generate a beginner-level coding challenge for {subject} on '{current_topic}'. Return only the problem statement."
        st.session_state[coding_key] = llm.ask_ai(challenge_prompt, language=subject)
    st.markdown(st.session_state[coding_key])

    user_code = st.text_area("Write your code here:", height=200)
    if st.button("Submit Code", key=f"submit_code_{viewing_index}"):
        feedback_prompt = f"Here is a student's solution for the challenge: {user_code}\n\nPlease give feedback and say if it's correct."
        feedback = llm.ask_ai(feedback_prompt, language=subject)
        st.info(feedback)

if not review_mode and viewing_index == topic_index:
    st.markdown("---")
    st.subheader("🌟 Check Your Understanding")
    quiz_key = f"quiz_{viewing_index}"
    if quiz_key not in st.session_state:
        with st.spinner("Creating a quick quiz..."):
            prompt = f"""
            Generate one multiple-choice question for the {subject} language on the topic '{current_topic}'.
            **INSTRUCTIONS:**
            1. If the question involves a code snippet, embed it directly in the 'question' string using Markdown.
            2. Return ONLY a valid JSON object with keys "question", "options" (a list of 4 strings), and "correct_answer" (the string of the correct option).
            """
            response = llm.ask_ai(prompt, language=subject)
            st.session_state[quiz_key] = json.loads(response)
    quiz_data = st.session_state[quiz_key]
    user_choice = st.radio(quiz_data['question'], quiz_data['options'], index=None)
    if st.button("Submit Answer"):
        if user_choice == quiz_data['correct_answer']:
            st.balloons(); st.success("Correct! You've unlocked the next topic!")
            db.update_progress(st.session_state['user_id'], subject, topic_index=topic_index + 1)
            st.session_state.viewing_topic_index = topic_index + 1
            st.rerun()
        else:
            st.error("Not quite. Try reviewing the lesson and answering again!")

st.markdown("---")
st.header("💬 AI Tutor Chat")
st.write(f"Ask any question about **{current_topic}** or general {subject} concepts.")
if 'chat_history' not in st.session_state: st.session_state.chat_history = []
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]): st.markdown(message["content"])
if user_prompt := st.chat_input(f"Ask me about {subject}..."):
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"): st.markdown(user_prompt)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            chat_prompt = f"The user is currently studying the topic '{current_topic}' in a {subject} course. They are at a '{current_level}' level. Answer the following user question in this context. User question: \"{user_prompt}\""
            ai_response = llm.ask_ai(chat_prompt, language=subject)
            st.markdown(ai_response)
    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})