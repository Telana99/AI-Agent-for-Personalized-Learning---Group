#!/usr/bin/env python3
"""
Demo script to showcase the difference between simple and agentic AI responses.
This demonstrates how the agentic approach provides better, more thoughtful responses.
"""

from ai_chat_helper import ask_ai_simple, ask_ai_advanced, get_advanced_tutor
import time

def demo_comparison():
    """Demonstrate the difference between simple and agentic responses"""
    
    print("🤖 AI Agentic Response Demo")
    print("=" * 50)
    
    # Sample questions for demonstration
    demo_questions = [
        "What are Python decorators and how do they work?",
        "Explain the difference between lists and tuples in Python",
        "How do I handle exceptions in Python?"
    ]
    
    user_level = "intermediate"
    user_name = "Demo Student"
    
    # Initialize advanced tutor
    tutor = get_advanced_tutor(user_name, user_level)
    
    for i, question in enumerate(demo_questions, 1):
        print(f"\n{'='*60}")
        print(f"Question {i}: {question}")
        print(f"{'='*60}")
        
        # Simple response
        print("\n📝 SIMPLE RESPONSE:")
        print("-" * 30)
        start_time = time.time()
        simple_answer = ask_ai_simple(question)
        simple_time = time.time() - start_time
        print(simple_answer)
        print(f"\n⏱️ Time taken: {simple_time:.2f} seconds")
        
        # Agentic response
        print("\n🤖 AGENTIC RESPONSE:")
        print("-" * 30)
        start_time = time.time()
        agentic_answer = ask_ai_advanced(question, user_level, user_name)
        agentic_time = time.time() - start_time
        print(agentic_answer)
        print(f"\n⏱️ Time taken: {agentic_time:.2f} seconds")
        
        print(f"\n📊 Comparison:")
        print(f"Simple: {simple_time:.2f}s | Agentic: {agentic_time:.2f}s")
        print(f"Time difference: {agentic_time - simple_time:.2f}s")
        
        input("\nPress Enter to continue to next question...")
    
    # Show learning analysis
    print(f"\n{'='*60}")
    print("📈 LEARNING ANALYSIS")
    print(f"{'='*60}")
    analysis = tutor.analyze_learning_patterns()
    print(analysis)

def demo_agentic_features():
    """Demonstrate specific agentic features"""
    
    print("\n🔍 AGENTIC FEATURES DEMO")
    print("=" * 50)
    
    user_level = "beginner"
    user_name = "Feature Demo"
    tutor = get_advanced_tutor(user_name, user_level)
    
    # Ask a series of related questions to show memory and context
    questions = [
        "What is a variable in Python?",
        "How do I create a variable?",
        "What's the difference between a variable and a constant?",
        "Can you give me an example of using variables in a function?"
    ]
    
    print(f"🤖 AI Agent will now answer {len(questions)} related questions...")
    print("Notice how each response builds on previous learning!")
    
    for i, question in enumerate(questions, 1):
        print(f"\n--- Question {i} ---")
        print(f"Q: {question}")
        print("\nA: ", end="")
        
        answer = ask_ai_advanced(question, user_level, user_name)
        print(answer)
        
        if i < len(questions):
            input("\nPress Enter for next question...")
    
    # Show the learning analysis
    print(f"\n{'='*60}")
    print("📊 LEARNING PROGRESS ANALYSIS")
    print(f"{'='*60}")
    analysis = tutor.analyze_learning_patterns()
    print(analysis)

if __name__ == "__main__":
    print("Welcome to the AI Agentic Response Demo!")
    print("This demo shows the difference between simple and agentic AI responses.")
    
    choice = input("\nChoose demo type:\n1. Comparison Demo\n2. Agentic Features Demo\n3. Both\nEnter choice (1-3): ")
    
    if choice == "1":
        demo_comparison()
    elif choice == "2":
        demo_agentic_features()
    elif choice == "3":
        demo_comparison()
        demo_agentic_features()
    else:
        print("Invalid choice. Running comparison demo...")
        demo_comparison()
    
    print("\n🎉 Demo completed! The agentic approach provides:")
    print("✅ More thoughtful and comprehensive responses")
    print("✅ Better context awareness and memory")
    print("✅ Adaptive learning based on user progress")
    print("✅ Quality self-assessment and iteration")
    print("✅ Personalized teaching approach") 