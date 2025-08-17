import streamlit as st
import sys
import os
import json
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from prompts.prompt_template import build_prompt
from ai_chat_helper import ask_ai

st.set_page_config(page_title="Learn C Programming", page_icon="📘", layout="wide")

# Hide sidebar/header
st.markdown("""
<style>
[data-testid="stSidebar"] { display: none; }
header[data-testid="stHeader"] { display: none; }
.block-container { padding-top: 2rem; padding-left: 4rem; padding-right: 4rem; }
</style>
""", unsafe_allow_html=True)

# --- Validate session ---
required_keys = ["user_name", "level", "course_topics_text", "topic_index"]
if not all(k in st.session_state for k in required_keys):
    st.error("🚫 Please start from the quiz page.")
    if st.button("⬅️ Back to Quiz"):
        st.switch_page("pages/c_quiz.py")
    st.stop()

# --- Load from session ---
user_name = st.session_state.user_name
user_level = st.session_state.level
topics_text = st.session_state.course_topics_text
topic_index = st.session_state.topic_index
language = "c"  # Fixed for now

# --- Convert learning path to list of topics ---
topics = []
for line in topics_text.strip().splitlines():
    if '.' in line:
        try:
            _, rest = line.split('.', 1)
            title, goal = rest.strip().split(" — ", 1) if " — " in rest else (rest.strip(), "")
            topics.append({"title": title.strip(), "goal": goal.strip()})
        except ValueError:
            continue

# --- All lessons completed ---
if topic_index >= len(topics):
    st.success("🎓 You've completed all lessons!")
    if st.button("⬅️ Back to Quiz"):
        st.switch_page("pages/c_quiz.py")
    st.stop()

# --- Current topic ---
topic = topics[topic_index]
st.title(f"📘 {topic['title']}")
st.subheader(f"🎯 Goal: {topic['goal']}")

# --- Lesson Caching ---
lesson_key = f"lesson_data_{topic_index}"
if lesson_key not in st.session_state:
    with st.spinner("Loading lesson..."):
        prompt = build_prompt(
            user_level=user_level,
            topic_title=topic["title"],
            topic_goal=topic["goal"],
            user_name=user_name,
            language=language,
        ) + """
        
Please provide only the lesson content. Do NOT include any quiz questions or exercises.  
Title and lesson should be appropriate.

💡 Important instructions:
- Provide explanations and code examples strictly in C programming language only.
- Do NOT include code snippets or examples in Python or any other languages.
- Use simple and clear C code to illustrate the concepts.
- Do NOT include any unrelated language examples.
- Keep the lesson content concise and focused on the topic.
"""
        lesson = ask_ai(prompt, language=language)
        st.session_state[lesson_key] = lesson
else:
    lesson = st.session_state[lesson_key]


st.write(lesson)

# --- Quiz Caching ---
quiz_key = f"quiz_data_{topic_index}"
if quiz_key not in st.session_state:
    with st.spinner("Creating quiz question..."):
        quiz_prompt = f"""
        You are an expert C programming tutor.

        Create a multiple-choice question (MCQ) for the topic "{topic['title']}" at the {user_level} level.
        Base it on the goal: "{topic['goal']}".

        Provide:
        1. The quiz question
        2. Four answer options (strings)
        3. The correct answer (match exactly one of the options)

        Do NOT label them a–d. Just provide 4 options in a list.

        Format your response as:
        {{
          "question": "...",
          "options": ["...", "...", "...", "..."],
          "correct_answer": "..."
        }}
        """
        quiz_json = ask_ai(quiz_prompt, language="json")

        try:
            parsed = json.loads(quiz_json)
            options = parsed["options"]
            correct = parsed["correct_answer"]
            random.shuffle(options)
            keys = ["a", "b", "c", "d"]
            quiz_options = dict(zip(keys, options))
            correct_key = next(k for k, v in quiz_options.items() if v.strip() == correct.strip())

            st.session_state[quiz_key] = {
                "question": parsed["question"],
                "options": quiz_options,
                "correct_key": correct_key
            }
        except Exception as e:
            st.error("❌ Failed to generate quiz.")
            if st.button("🔄 Try Again"):
                st.rerun()
            st.stop()

# --- Show Quiz ---
quiz_data = st.session_state[quiz_key]
st.markdown("### 🌟 Quiz Time 🌟")
opt_texts = [f"{k}) {v}" for k, v in quiz_data["options"].items()]
user_answer = st.radio(quiz_data["question"], opt_texts)

if "quiz_passed" not in st.session_state:
    st.session_state.quiz_passed = False

if st.button("Submit Answer"):
    selected = user_answer[0]
    if selected == quiz_data["correct_key"]:
        st.success("Correct! 🎉")
        st.session_state.quiz_passed = True
    else:
        st.error("Oops, try again.")
        st.session_state.quiz_passed = False

# --- Continue ---
if st.session_state.quiz_passed:
    if topic_index + 1 < len(topics):
        if st.button("➡️ Continue to Next Lesson"):
            st.session_state.topic_index += 1
            st.session_state.quiz_passed = False

            for key in [f"quiz_data_{topic_index+1}", f"lesson_data_{topic_index+1}"]:
                st.session_state.pop(key, None)

            st.rerun()
    else:
        st.success("🎓 All lessons completed!")

# --- Ask AI ---
st.markdown("---")
st.markdown("### 💬 Ask anything about C Programming")
q = st.text_input("Your question:")
if q:
    with st.spinner("Thinking..."):
        ans = ask_ai(q, language=language)
    st.markdown("**AI Tutor says:**")
    st.write(ans)

# --- Back to Home ---
if st.button("⬅️ Back to Home"):
    st.switch_page("pages/home.py")