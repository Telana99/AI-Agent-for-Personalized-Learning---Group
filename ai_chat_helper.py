import openai
import os
from dotenv import load_dotenv
import json
import time
from datetime import datetime


load_dotenv()
print("API Key Loaded:", os.getenv("OPENROUTER_API_KEY"))


client = openai.OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)

class AgenticTutor:
    def __init__(self, user_name="Student", user_level="beginner"):
        self.user_name = user_name
        self.user_level = user_level
        self.conversation_history = []
        self.learning_progress = {
            "topics_covered": [],
            "difficulties_identified": [],
            "strengths_identified": [],
            "recommendations": []
        }
        self.response_quality_history = []
    
    def add_to_history(self, question, answer, quality_score=None):
        """Add interaction to conversation history"""
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answer": answer,
            "quality_score": quality_score
        })
    
    def analyze_learning_patterns(self):
        """Analyze conversation history to identify learning patterns"""
        if len(self.conversation_history) < 2:
            return "Insufficient data for pattern analysis"
        
        analysis_prompt = f"""
Analyze this conversation history for {self.user_name} (a {self.user_level} student):

{json.dumps(self.conversation_history, indent=2)}

Identify:
1. Learning patterns and progress
2. Common difficulties or misconceptions
3. Strengths and areas of confidence
4. Recommended next topics or approaches

Provide insights in a structured format.
"""
        
        try:
            analysis_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.3
            )
            return analysis_response.choices[0].message.content
        except Exception as e:
            return f"Analysis failed: {e}"
    
    def create_adaptive_response(self, user_question, max_iterations=3):
        """
        Advanced agentic response with memory, context, and adaptive learning.
        """
        
        print(f"\n🤖 AI Agent is thinking... (max {max_iterations} iterations)")
        
        # Step 1: CONTEXT ANALYSIS
        context_prompt = f"""
You are an AI tutor for {self.user_name}, a {self.user_level} level Python student.

CURRENT CONTEXT:
- User Level: {self.user_level}
- Previous interactions: {len(self.conversation_history)} questions
- Recent topics: {[h['question'][:50] + '...' for h in self.conversation_history[-3:]] if self.conversation_history else 'None'}

NEW QUESTION: "{user_question}"

ANALYZE:
1. How does this question relate to previous learning?
2. What level of understanding does it indicate?
3. Are there any misconceptions or gaps to address?
4. What would be the most effective teaching approach?

Provide a brief context analysis.
"""
        
        print("🔍 Step 1: Analyzing context and learning patterns...")
        context_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": context_prompt}],
            temperature=0.2
        )
        context_analysis = context_response.choices[0].message.content
        
        # Step 2: STRATEGIC PLANNING
        planning_prompt = f"""
Based on the context analysis:
{context_analysis}

Create a detailed response strategy for: "{user_question}"

Strategy should include:
1. Core concepts to explain
2. Examples that match {self.user_name}'s level
3. How to connect to previous learning
4. Potential misconceptions to address
5. Engagement techniques for {self.user_level} level
6. Assessment of understanding

Format as a structured plan.
"""
        
        print("📋 Step 2: Creating strategic response plan...")
        plan_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": planning_prompt}],
            temperature=0.3
        )
        plan = plan_response.choices[0].message.content
        
        # Step 3: EXECUTE with memory
        execution_prompt = f"""
STRATEGIC PLAN:
{plan}

CONTEXT:
{context_analysis}

Generate a comprehensive response to: "{user_question}"

Requirements:
- Follow the strategic plan exactly
- Reference previous learning when relevant
- Use {self.user_level}-appropriate language
- Include practical examples
- Be encouraging and supportive
- Structure logically for {self.user_name}'s learning style
"""
        
        print("⚡ Step 3: Executing strategic response...")
        execution_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": execution_prompt}],
            temperature=0.7
        )
        initial_response = execution_response.choices[0].message.content
        
        # Step 4: REFLECT and ITERATE with quality metrics
        current_response = initial_response
        iteration_count = 1
        
        while iteration_count < max_iterations:
            reflection_prompt = f"""
CRITICALLY EVALUATE this response to "{user_question}" for {self.user_name} ({self.user_level} level):

RESPONSE:
{current_response}

CONTEXT:
{context_analysis}

Rate on these criteria (1-10):
1. Accuracy and correctness
2. Clarity for {self.user_level} level
3. Completeness of explanation
4. Practical usefulness
5. Engagement and motivation
6. Connection to previous learning
7. Addressing potential misconceptions

If ALL scores are 8+ and the response is excellent, say "EXCELLENT". 
Otherwise, provide specific, actionable improvement suggestions.
"""
            
            print(f"🔍 Step 4.{iteration_count}: Advanced reflection and quality assessment...")
            reflection_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": reflection_prompt}],
                temperature=0.2
            )
            reflection = reflection_response.choices[0].message.content
            
            if "EXCELLENT" in reflection.upper():
                print(f"✅ Response quality is excellent! Finalizing...")
                break
            
            # Step 5: ITERATE with learning adaptation
            improvement_prompt = f"""
CURRENT RESPONSE:
{current_response}

REFLECTION FEEDBACK:
{reflection}

CONTEXT:
{context_analysis}

Generate an improved version that:
- Addresses ALL specific issues identified in reflection
- Maintains the good parts of the original
- Better adapts to {self.user_name}'s learning style
- Improves clarity and engagement
- Connects better to previous learning
"""
            
            print(f"🔄 Step 5.{iteration_count}: Iterating with adaptive improvements...")
            improvement_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": improvement_prompt}],
                temperature=0.6
            )
            current_response = improvement_response.choices[0].message.content
            iteration_count += 1
        
        # Step 6: FINALIZE with learning insights
        final_prompt = f"""
Finalize this response for {self.user_name} ({self.user_level} level):

{current_response}

Add:
1. A brief learning summary
2. Connection to future topics
3. Encouragement for continued learning
4. Suggestion for next steps

Keep it friendly, supportive, and motivating.
"""
        
        print("🎯 Step 6: Finalizing with learning insights...")
        final_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": final_prompt}],
            temperature=0.5
        )
        final_answer = final_response.choices[0].message.content
        
        # Step 7: UPDATE LEARNING PROGRESS
        self.add_to_history(user_question, final_answer)
        
        print(f"✅ AI Agent completed {iteration_count} iteration(s)")
        print(f"📊 Learning progress tracked: {len(self.conversation_history)} interactions")
        
        return final_answer

def ask_ai_simple(question):
    """Simple direct response - kept for comparison"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a friendly Python tutor who explains things in simple ways with examples."},
            {"role": "user", "content": question}
        ]
    )
    
    return response.choices[0].message.content

def create_agentic_response(user_question, user_level="beginner", user_name="Student", max_iterations=3):
    """
    Agentic AI response system with planning, execution, reflection, and iteration.
    
    The agent follows this process:
    1. PLAN: Analyze the question and create a response strategy
    2. EXECUTE: Generate an initial response based on the plan
    3. REFLECT: Evaluate the quality and completeness of the response
    4. ITERATE: If needed, improve the response based on reflection
    5. DELIVER: Provide the final refined response
    """
    
    print(f"\n🤖 AI Agent is thinking... (max {max_iterations} iterations)")
    
    # Step 1: PLAN
    planning_prompt = f"""
You are an AI tutor for {user_name}, a {user_level} level Python student.

ANALYZE this question: "{user_question}"

Create a detailed response plan that includes:
1. What concepts need to be explained
2. What examples would be most helpful
3. How to structure the explanation for a {user_level} level
4. What potential misconceptions to address
5. How to make it engaging and memorable

Format your plan as a structured list.
"""
    
    print("📋 Step 1: Planning response strategy...")
    plan_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": planning_prompt}],
        temperature=0.3
    )
    plan = plan_response.choices[0].message.content
    
    # Step 2: EXECUTE
    execution_prompt = f"""
Based on this plan:
{plan}

Generate a comprehensive response to: "{user_question}"

Requirements:
- Follow the plan exactly
- Use clear, {user_level}-appropriate language
- Include practical examples
- Be encouraging and supportive
- Structure the response logically
"""
    
    print("⚡ Step 2: Executing initial response...")
    execution_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": execution_prompt}],
        temperature=0.7
    )
    initial_response = execution_response.choices[0].message.content
    
    # Step 3: REFLECT and ITERATE
    current_response = initial_response
    iteration_count = 1
    
    while iteration_count < max_iterations:
        reflection_prompt = f"""
CRITICALLY EVALUATE this response to the question "{user_question}":

{current_response}

Rate the response on these criteria (1-10):
1. Accuracy and correctness
2. Clarity and understandability for a {user_level} student
3. Completeness of explanation
4. Practical usefulness
5. Engagement and motivation

Identify specific areas for improvement. If the response is excellent (8+ on all criteria), say "EXCELLENT". Otherwise, provide specific suggestions for improvement.
"""
        
        print(f"🔍 Step 3.{iteration_count}: Reflecting on response quality...")
        reflection_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": reflection_prompt}],
            temperature=0.2
        )
        reflection = reflection_response.choices[0].message.content
        
        if "EXCELLENT" in reflection.upper():
            print(f"✅ Response quality is excellent! Finalizing...")
            break
        
        # Step 4: ITERATE
        improvement_prompt = f"""
The current response to "{user_question}" is:
{current_response}

The reflection identified these areas for improvement:
{reflection}

Generate an improved version that addresses these specific issues while maintaining the good parts of the original response.
"""
        
        print(f"🔄 Step 4.{iteration_count}: Iterating to improve response...")
        improvement_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": improvement_prompt}],
            temperature=0.6
        )
        current_response = improvement_response.choices[0].message.content
        iteration_count += 1
    
    # Step 5: DELIVER
    final_prompt = f"""
Finalize this response for {user_name} (a {user_level} student):

{current_response}

Add a brief summary and encourage further questions. Keep it friendly and supportive.
"""
    
    print("🎯 Step 5: Finalizing and delivering response...")
    final_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": final_prompt}],
        temperature=0.5
    )
    final_answer = final_response.choices[0].message.content
    
    print(f"✅ AI Agent completed {iteration_count} iteration(s)")
    
    return final_answer

def ask_ai(question, user_level="beginner", user_name="Student"):
    """
    Main function that uses the agentic approach for better responses.
    Falls back to simple response if there are any issues.
    """
    try:
        return create_agentic_response(question, user_level, user_name)
    except Exception as e:
        print(f"⚠️ Agentic approach failed, falling back to simple response: {e}")
        return ask_ai_simple(question)

# Global tutor instance for advanced features
_advanced_tutor = None

def get_advanced_tutor(user_name="Student", user_level="beginner"):
    """Get or create an advanced tutor instance with memory and learning tracking"""
    global _advanced_tutor
    if _advanced_tutor is None:
        _advanced_tutor = AgenticTutor(user_name, user_level)
    return _advanced_tutor

def ask_ai_advanced(question, user_level="beginner", user_name="Student"):
    """
    Advanced agentic response with memory, context, and adaptive learning.
    """
    tutor = get_advanced_tutor(user_name, user_level)
    return tutor.create_adaptive_response(question)