import streamlit as st
import json
import sys
import os
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from ai_chat_helper import ask_ai

st.set_page_config(page_title="C Level Diagnostic", page_icon="🧠", layout="wide")

st.markdown("""
<style>
[data-testid="stSidebar"] { display: none; }
header[data-testid="stHeader"] { display: none; }
.block-container { padding-top: 2rem; padding-left: 4rem; padding-right: 4rem; }
</style>
""", unsafe_allow_html=True)

# Reset handling
if st.session_state.get("refresh_quiz", False):
    for key in ["quiz_started", "scores", "level", "course_topics_text", "answers"]:
        st.session_state.pop(key, None)
    st.session_state.refresh_quiz = False
    st.rerun()

# Session init
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False
if "scores" not in st.session_state:
    st.session_state.scores = {"beginner": 0, "intermediate": 0, "advanced": 0}
if "level" not in st.session_state:
    st.session_state.level = None

st.title("🧠 C Programming Adaptive Level Quiz")

# Start button
if not st.session_state.quiz_started:
    if st.button("Start Quiz"):
        st.session_state.quiz_started = True
    st.stop()

st.subheader("📝 Answer the following multiple-choice questions")
st.markdown("We'll adapt the difficulty based on your performance.")

### --- Question Generator ---
def generate_question(difficulty):
    prompt = f"""
You are an expert C programming tutor.

Generate a multiple-choice question (MCQ) to assess C programming knowledge.

The difficulty level is **{difficulty}**.

Only return valid pure JSON, no markdown or commentary.

Format:
{{
  "question": "Your question here?",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "correct_answer": "One of the options exactly as written"
}}
"""

    try:
        response = ask_ai(prompt, language="json")

        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            st.error(f"❌ JSON decode failed for difficulty: {difficulty}")
            st.code(response)
            raise ValueError("Invalid JSON from AI")

        options = data["options"]
        if not options or len(options) != 4:
            raise ValueError("Expected 4 options in MCQ")

        random.shuffle(options)
        keys = ["a", "b", "c", "d"]
        options_dict = dict(zip(keys, options))

        correct_key = next(
            k for k, v in options_dict.items()
            if v.strip() == data["correct_answer"].strip()
        )

        return {
            "question": data["question"],
            "options": options_dict,
            "correct_key": correct_key
        }

    except Exception as e:
        st.warning(f"⚠️ AI failed for {difficulty} level. Using static fallback question. Error: {e}")
        fallback = {
            "beginner": {
                "question": "Which of the following is a valid keyword in C?",
                "options": {"a": "function", "b": "define", "c": "int", "d": "include"},
                "correct_key": "c"
            },
            "intermediate": {
                "question": "What will the expression *ptr++ do?",
                "options": {"a": "Increment the value pointed to by ptr",
                            "b": "Move pointer to next memory location",
                            "c": "De-reference and then increment pointer",
                            "d": "Invalid syntax"},
                "correct_key": "c"
            },
            "advanced": {
                "question": "Which function is used to deallocate memory allocated by malloc?",
                "options": {"a": "dealloc()", "b": "free()", "c": "delete()", "d": "remove()"},
                "correct_key": "b"
            }
        }
        return fallback.get(difficulty, fallback["beginner"])

# Load questions if not already generated
if "answers" not in st.session_state:
    with st.spinner("Generating questions..."):
        st.session_state.answers = {
            "beginner": [None]*3,
            "intermediate": [None]*3,
            "advanced": [None]*3
        }
        st.session_state.questions = {
            "beginner": [generate_question("beginner") for _ in range(3)],
            "intermediate": [generate_question("intermediate") for _ in range(3)],
            "advanced": [generate_question("advanced") for _ in range(3)],
        }

# Show beginner questions
st.markdown("### 🟢 Beginner Level")
for i, q in enumerate(st.session_state.questions["beginner"]):
    st.markdown(f"**Q{i+1}. {q['question']}**")
    opts = [f"{k}) {q['options'][k]}" for k in q['options']]
    selected = st.radio("", opts, key=f"b_q{i}")
    st.session_state.answers["beginner"][i] = selected[0] if selected else None

# Submit beginner level
if st.button("Submit Beginner Answers"):
    score = sum(
        1 for i, q in enumerate(st.session_state.questions["beginner"])
        if st.session_state.answers["beginner"][i] == q["correct_key"]
    )
    st.session_state.scores["beginner"] = score
    st.rerun()

# If passed beginner level
if st.session_state.scores["beginner"] >= 3:
    st.markdown("### 🟡 Intermediate Level")
    for i, q in enumerate(st.session_state.questions["intermediate"]):
        st.markdown(f"**Q{i+1}. {q['question']}**")
        opts = [f"{k}) {q['options'][k]}" for k in q['options']]
        selected = st.radio("", opts, key=f"i_q{i}")
        st.session_state.answers["intermediate"][i] = selected[0] if selected else None

    if st.button("Submit Intermediate Answers"):
        score = sum(
            1 for i, q in enumerate(st.session_state.questions["intermediate"])
            if st.session_state.answers["intermediate"][i] == q["correct_key"]
        )
        st.session_state.scores["intermediate"] = score
        st.rerun()

# If passed intermediate level
if st.session_state.scores["intermediate"] >= 3:
    st.markdown("### 🔵 Advanced Level")
    for i, q in enumerate(st.session_state.questions["advanced"]):
        st.markdown(f"**Q{i+1}. {q['question']}**")
        opts = [f"{k}) {q['options'][k]}" for k in q['options']]
        selected = st.radio("", opts, key=f"a_q{i}")
        st.session_state.answers["advanced"][i] = selected[0] if selected else None

    if st.button("Submit Advanced Answers"):
        score = sum(
            1 for i, q in enumerate(st.session_state.questions["advanced"])
            if st.session_state.answers["advanced"][i] == q["correct_key"]
        )
        st.session_state.scores["advanced"] = score
        st.rerun()

### --- Final Level Detection ---
total = st.session_state.scores
if sum(total.values()) > 0:
    level = "beginner"

    if total["beginner"] == 3:
        if total["intermediate"] == 3:
            level = "advanced"
        else:
            level = "intermediate"

    st.session_state.level = level


if st.session_state.level:
    st.success(f"🎉 Based on your answers, you are at **{st.session_state.level.capitalize()}** level.")

    # Show scores
    st.markdown("### 🧾 Your Quiz Scores")
    st.write(total)

    # Ask for name
    name = st.text_input("What's your name?", key="username_input")
    if name:
        st.session_state.user_name = name

        # AI-powered textual course outline (plain text, not JSON)
        if "course_topics_text" not in st.session_state:
            with st.spinner("Generating personalized learning path..."):
                outline_prompt = f"""
You are an expert C programming teacher.

Generate a clear, easy-to-read learning path for a student at the **{st.session_state.level}** level in C programming.

Format it as a numbered list, with each line containing the topic name and a short description of what the student will learn.

Example format:

1. Variables and Data Types — Understand the basic data types and how to declare variables.
2. Control Structures — Learn if-else, loops, and switch-case statements.
3. Functions — Understand how to write and use functions.

Please provide 3 topics.
"""

                response = ask_ai(outline_prompt, language="text")
                st.session_state.course_topics_text = response

        st.markdown("### 📘 Your Personalized Learning Path")
        st.markdown(st.session_state.course_topics_text)

        if st.button("Start First Lesson"):
            st.session_state.selected_topic = None  # or adapt as needed for your learn.py
            st.session_state.topic_index = 0
            st.switch_page("pages/learn.py")





