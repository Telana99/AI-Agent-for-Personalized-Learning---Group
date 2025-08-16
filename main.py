import json
from prompts.prompt_template import build_prompt
from ai_agents.user_question_answerer import QuestionAnswererAgent
from ai_agents.course_content_create_agent import ContentCreateAgent
from ai_chat_helper import ask_ai
import os

language = input("Which programming language do you want to learn? (C/Python): ").strip().lower()

supported_languages = ['python', 'c']
if language not in supported_languages:
    print(f"Sorry, {language} is not supported yet.")
    exit()

#Load dynamic course content and prompt path
course_file = f"course_contents/course_{language}.json"
prompt_file = f"language_prompts/prompt_{language}.txt"


# Load course content
if not os.path.exists(course_file):
    print(f"Missing course file: {course_file}")
    exit()

with open(course_file) as f:
    course = json.load(f)

# Step 1: Ask some  questions

score = 0

print("Welcome to the {language} Level Checker!")
print("Answer these 3 questions to find your skill level.")

# Question 1
answer1 = input("1. What is the correct syntax to declare an integer variable in C? ")
if "int" in answer1.lower():
    score += 1

# Question 2
print("2. What will be the output of the following code?")
print("""
int a = 5;
int b = 2;
float c = a / b;
printf(\"%.2f\", c);
""")
answer2 = input("Your answer: ")
if answer2.strip() == "2.00":
    score += 1

# Question 3
answer3 = input("3. What is the purpose of the 'const' keyword in C? ")
if "read-only" in answer3.lower() or "constant" in answer3.lower() or "cannot be changed" in answer3.lower():
    score += 1

# Determine level
if score == 3:
    level = "Advanced"
elif score == 2:
    level = "Intermediate"
else:
    level = "Beginner"

print(f"\nYour {language.capitalize()} level is: {level}")
print("\nHere's your personalized learning path:")

# Show topics based on level
user_level = level.lower()
user_name = input("\nBefore we continue, what's your name? ")

for idx, topic in enumerate(course[user_level], start=1):
    print(f"{idx}. {topic['title']} — {topic['goal']}")

# Step 2: Teach the first topic using prompt engineering
print("\n Let's begin learning with the first topic!")

lesson_create_agent = ContentCreateAgent()

lesson = lesson_create_agent.create_content(user_name=user_name, user_level=user_level, language=language)

print("\n AI Tutor says:\n")
print(lesson)

# Step 3: Allow user to ask questions
print(f"\nNow you can ask {language.capitalize()} questions. Type 'exit' to stop.")

chat_history = ''
answer_question_agent = QuestionAnswererAgent()
while True:
    user_question = input(f"\nAsk a {language.capitalize()} question: ")
    if user_question.lower().strip() in ["exit", "quit", "no", ""]:
        print("Goodbye! Happy coding 😊")
        break

    answer = answer_question_agent.answer_user_question(user_question, language=language, user_name=user_name, user_level=user_level, chat_history=chat_history)

    print("\nAI Tutor says:\n")
    print(f"Response: {answer.response}")
    print(f"\nExplanation: {answer.explanation}")
    
    if answer.examples:
        print("\n💻 Code Examples:")
        for i, example in enumerate(answer.examples, 1):
            print(f"\nExample {i}:")
            print(example)
    
    if answer.related_topics:
        print(f"\n🔗 Related Topics: {', '.join(answer.related_topics)}")
        
    chat_history = f"{user_question}: {answer.response}"

