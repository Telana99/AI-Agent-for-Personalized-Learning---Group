import streamlit as st
import json
import sys
import os
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from ai_chat_helper import ask_ai

st.set_page_config(page_title="C Programming Quiz", page_icon="🧠", layout="wide")

# Hide sidebar/header
st.markdown("""
<style>
[data-testid="stSidebar"] {
    display: none;
}
header[data-testid="stHeader"] {
    display: none;
}
.block-container {
    padding-top: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
}
</style>
""", unsafe_allow_html=True)

# Check if coming from home page or manually resetting the quiz
if st.session_state.get("refresh_quiz", False):
    for key in ["quiz_started", "score", "level", "dynamic_quiz", "answers"]:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.refresh_quiz = False
    st.rerun()


# Initialize session state
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False
if "score" not in st.session_state:
    st.session_state.score = 0
if "level" not in st.session_state:
    st.session_state.level = None
if "language" not in st.session_state:
    st.session_state.language = "c"

st.title("🧠 C Programming Level Checker")

# Step 1: Start Quiz
if not st.session_state.quiz_started:
    if st.button("Start Quiz"):
        st.session_state.quiz_started = True
    st.stop()

st.subheader("Answer these 3 questions to find your C programming level")

# --- Dynamic Quiz Generation ---
def generate_question():
    prompt = """
You are an expert C programming tutor.

Generate a multiple-choice question (MCQ) to assess C programming knowledge.
Make sure it's appropriate for a general level diagnostic quiz.

Format:
{
  "question": "Question text",
  "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
  "correct_answer": "The correct option"
}
"""
    try:
        response = ask_ai(prompt, language="json")
        data = json.loads(response)
        options = data["options"]
        random.shuffle(options)
        option_keys = ["a", "b", "c", "d"]
        options_dict = dict(zip(option_keys, options))
        correct_key = next(k for k, v in options_dict.items() if v.strip() == data["correct_answer"].strip())
        return {
            "question": data["question"],
            "options": options_dict,
            "correct_key": correct_key
        }
    except Exception as e:
        st.error("❌ Failed to generate quiz question.")

        print(e)
        st.stop()

# Generate quiz once
if "dynamic_quiz" not in st.session_state:
    with st.spinner("Generating your quiz..."):
        st.session_state.dynamic_quiz = [generate_question() for _ in range(3)]
    st.session_state.answers = [None, None, None]

score = 0
quiz = st.session_state.dynamic_quiz

# Show quiz
for i, q in enumerate(quiz):
    st.markdown(f"**Q{i+1}. {q['question']}**")
    keys = list(q["options"].keys())
    values = [f"{k}) {q['options'][k]}" for k in keys]
    selected = st.radio("", values, key=f"q{i}")
    st.session_state.answers[i] = selected[0] if selected else None

# Submit
if st.button("Submit Quiz"):
    for i, q in enumerate(quiz):
        if st.session_state.answers[i] == q["correct_key"]:
            score += 1

    st.session_state.score = score

    if score == 3:
        st.session_state.level = "advanced"
    elif score == 2:
        st.session_state.level = "intermediate"
    else:
        st.session_state.level = "beginner"

    st.rerun()

# Step 2: Show level & continue
if st.session_state.level:
    st.success(f"🎉 You are at **{st.session_state.level.capitalize()}** level.")

    user_name = st.text_input("Before we continue, what's your name?")
    if user_name:
        st.session_state.user_name = user_name
        lang = st.session_state.language
        course_file = f"course_contents/course_{lang}.json"

        if not os.path.exists(course_file):
            st.error(f"Missing course file: {course_file}")
            st.stop()

        with open(course_file) as f:
            course = json.load(f)

        user_level = st.session_state.level
        st.session_state.course = course
        st.markdown("### 📘 Your Personalized Learning Path")

        for idx, topic in enumerate(course[user_level], start=1):
            st.write(f"{idx}. {topic['title']} — {topic['goal']}")

        if st.button("Start First Lesson"):
            st.session_state.selected_topic = course[user_level][0]
            st.session_state.topic_index = 0
            st.session_state.user_level = user_level
            st.session_state.language = lang
            st.switch_page("pages/learn.py")
