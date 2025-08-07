import json
from prompts.prompt_template import build_prompt
from ai_chat_helper import ask_ai_advanced, get_advanced_tutor


#Load course content
with open("course_content.json") as f:
    course = json.load(f)


# Step 1: Ask some Python questions

score = 0

print("Welcome to the Python Level Checker!")
print("Answer these 3 questions to find your skill level.")

# Question 1
answer1 = input("1. What is the output of: print(2 + 3 * 4)? ")
if answer1 == "14":
    score += 1

# Question 2
answer2 = input("2. What keyword is used to define a function in Python? ")
if answer2.lower() == "def":
    score += 1

# Question 3
answer3 = input("3. What does 'len()' do in Python? ")
if "length" in answer3.lower():
    score += 1

# Determine level
if score == 3:
    level = "Advanced"
elif score == 2:
    level = "Intermediate"
else:
    level = "Beginner"

print(f"\nYour Python level is: {level}")
# Suggest topics based on the user's level
print("\nHere's your personalized Python learning path:")

# Show topics based on level
user_level = level.lower()
user_name = input("\nBefore we continue, what's your name? ")

for idx, topic in enumerate(course[user_level], start=1):
    print(f"{idx}. {topic['title']} — {topic['goal']}")

# Step 2: Teach the first topic using prompt engineering
print("\n🧠 Let's begin learning with the first topic!")

first_topic = course[user_level][0]
prompt = build_prompt(
    user_level=level,
    topic_title=first_topic["title"],
    topic_goal=first_topic["goal"],
    user_name=user_name
)

# Initialize advanced tutor with memory
tutor = get_advanced_tutor(user_name, user_level)

lesson = ask_ai_advanced(prompt, user_level=user_level, user_name=user_name)
print("\n📘 AI Tutor says:\n")
print(lesson)

print("\nNow you can ask Python questions. Type 'exit' to stop.")
print("🤖 The AI Agent will now think through each response carefully!")
print("📊 Your learning progress is being tracked and analyzed!")

while True:
    user_question = input("\nAsk a Python question: ")
    if user_question.lower().strip() == "exit":
        # Show learning analysis before exiting
        print("\n📈 Learning Analysis:")
        analysis = tutor.analyze_learning_patterns()
        print(analysis)
        print("\nGoodbye! Happy coding 😊")
        break

    answer = ask_ai_advanced(user_question, user_level=user_level, user_name=user_name)
    print("\nAI Tutor says:\n")
    print(answer)
