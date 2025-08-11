import json
from prompts.prompt_template import build_prompt
from ai_agents.user_question_answerer import QuestionAnswererAgent
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
answer1 = input(f"\n1. What is the correct syntax to declare an integer variable in {language}? ")
if "int" in answer1.lower():
    score += 1

# Question 2
# Define syntax templates for each language
# Syntax templates
syntax_map = {
    "c": {
        "declare_int": "int {var} = {value};",
        "declare_float": "float {var} = {value};",
        "print": 'printf("%.2f", {var});'
    },
    "python": {
        "declare_int": "{var} = {value}",
        "declare_float": "{var} = {value}",
        "print": 'print(f"{{{var}:.2f}}")'
    }
}

def generate_code(language):
    lang = syntax_map.get(language)
    if not lang:
        return "Language not supported."
    code = [
        lang["declare_int"].format(var="a", value=5),
        lang["declare_int"].format(var="b", value=2),
        lang["declare_float"].format(var="c", value="a / b"),
        lang["print"].format(var="c")
    ]
    return "\n".join(code)

    # Syntax templates
syntax_map = {
    "c": {
        "declare_int": "int {var} = {value};",
        "declare_float": "float {var} = {value};",
        "print": 'printf("%.2f", {var});'
    },
    "python": {
        "declare_int": "{var} = {value}",
        "declare_float": "{var} = {value}",
        "print": 'print(f"{{{var}:.2f}}")'
    }
}

def generate_code(language):
    lang = syntax_map.get(language)
    if not lang:
        return "Language not supported."
    code = [
        lang["declare_int"].format(var="a", value=5),
        lang["declare_int"].format(var="b", value=2),
        lang["declare_float"].format(var="c", value="a / b"),
        lang["print"].format(var="c")
    ]
    return "\n".join(code)

# Question 2
print("2. What will be the output of the following code?")
print(generate_code(language))


# # Question 2
# print("2. What will be the output of the following code?")
# print(generate_code(language))

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

first_topic = course[user_level][0]

prompt = build_prompt(
    user_level=level,
    topic_title=first_topic["title"],
    topic_goal=first_topic["goal"],
    user_name=user_name,
    language=language
)


lesson = ask_ai(prompt, language)
print("\n AI Tutor says:\n")
print(lesson)

# Step 3: Allow user to ask questions
print(f"\nNow you can ask {language.capitalize()} questions. Type 'exit' to stop.")
agent = QuestionAnswererAgent()

while True:
    user_question = input(f"\nAsk a {language} question: ")
    if user_question.lower().strip() == "exit":
        print("Goodbye! Happy coding 😊")
        break

    answer = agent.answer_user_question(question=user_question, language=language, user_level=user_level, user_name=user_name)

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

