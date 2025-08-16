import openai
import os
import json
import re
import logging
from typing import Dict, Any, List
from dataclasses import dataclass

# Configure logging
import os
SHOW_INFO_LOGS = os.getenv("SHOW_INFO_LOGS", "False").lower() == "true"

if SHOW_INFO_LOGS:
    logging.basicConfig(level=logging.INFO)
else:
    logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

@dataclass
class Content:
    lesson: str
    explanation: str
    examples: List[str]
    related_topics: List[str]

class ContentCreateAgent:
    """
    AI Agent for creating course content for user based on the user level.
    Creates personalized lessons based on course JSON structure and user skill level.
    """
    
    def __init__(self, api_key: str = None):
        """Initialize the content creation agent."""
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        
        if not self.api_key:
            logger.warning("No API key found. Set OPENROUTER_API_KEY environment variable")
            self.client = None
        else:
            self.client = openai.OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key
            )
        
        # Answer styles for different levels
        self.content_styles = {
            "beginner": {
                "tone": "Explain simply like teaching an 11-year-old. Use simple words and real-life examples. Be friendly and supportive.",
                "complexity": "Simple explanations with analogies",
                "examples": "Basic, step-by-step examples",
                "detail": "Thorough explanations"
            },
            "intermediate": {
                "tone": "Use clear technical terms and explain with real code examples. Help the student connect concepts.",
                "complexity": "Clear technical explanations",
                "examples": "Practical, real-world examples",
                "detail": "Balanced explanations"
            },
            "advanced": {
                "tone": "Go deep. Include theory, use real programming terms, mention best practices and ask thought-provoking questions.",
                "complexity": "Advanced concepts and best practices",
                "examples": "Complex scenarios and optimization",
                "detail": "Concise but comprehensive"
            }
        }
        
        # Knowledge sources for different languages
        self.knowledge_sources = {
            "python": [
                "Python Official Documentation (docs.python.org)",
                "Real Python Tutorials",
                "Python.org Tutorial",
                "W3Schools Python",
                "GeeksforGeeks Python"
            ],
            "c": [
                "C Programming Official Documentation",
                "GeeksforGeeks C Programming",
                "W3Schools C Tutorial",
                "C Tutorial Point",
                "Learn-C.org"
            ]
        }
    
    def create_content(self, user_name: str, user_level: str, language: str) -> str:
        """
        Create course content based on user level and language with iterative improvement.
        
        Args:
            user_name: User's name
            user_level: User's skill level (beginner/intermediate/advanced)
            language: Programming language (python/c)
            
        Returns:
            Complete lesson content as a string
        """
        logger.info(f"Creating content for {user_name} at {user_level} level in {language}")
        
        # Load course content for the specific language
        course_file = f"course_contents/course_{language}.json"
        
        if not os.path.exists(course_file):
            logger.error(f"Missing course file: {course_file}")
            return f"Sorry, I couldn't find the course content for {language}."
        
        with open(course_file) as f:
            course = json.load(f)
        
        # Get the first topic for the user's level
        if user_level.lower() not in course:
            logger.error(f"Invalid user level: {user_level}")
            return f"Sorry, I couldn't determine the appropriate content for your level."
        
        user_topics = course[user_level.lower()]
        if not user_topics:
            logger.error(f"No topics found for level: {user_level}")
            return f"Sorry, no topics are available for your current level."
        
        first_topic = user_topics[0]
        topic_title = first_topic["title"]
        topic_goal = first_topic["goal"]
        
        # Iterative improvement process
        max_iterations = 3
        best_content = None
        best_score = 0.0
        previous_feedback = ""
        
        logger.info(f"Starting iterative content improvement for {topic_title}")
        
        for iteration in range(max_iterations):
            logger.info(f"Content generation iteration {iteration + 1}/{max_iterations}")
            
            # Generate lesson content
            lesson_content = self._generate_lesson_content(
                user_name=user_name,
                user_level=user_level,
                language=language,
                topic_title=topic_title,
                topic_goal=topic_goal,
                iteration=iteration,
                previous_feedback=previous_feedback
            )
            
            # Evaluate content quality
            score = self._evaluate_content_quality(
                lesson_content, topic_title, topic_goal, language, user_level
            )
            
            logger.info(f"Iteration {iteration + 1} score: {score:.2f}/1.0")
            
            if score > best_score:
                best_score = score
                best_content = lesson_content
                logger.info(f"New best score achieved: {score:.2f}")
            
            # Generate feedback for next iteration if needed
            if iteration < max_iterations - 1 and score < 0.85:
                previous_feedback = self._generate_improvement_feedback(
                    lesson_content, score, topic_title, user_level
                )
                logger.info(f"Improvement feedback for next iteration: {previous_feedback[:100]}...")
            
            # If score is high enough, break early
            if score > 0.85:
                logger.info(f"High quality content achieved (score: {score:.2f}), stopping iterations")
                break
        
        if best_content is None:
            # Fallback to basic lesson
            logger.warning("All iterations failed, using fallback lesson")
            best_content = self._create_fallback_lesson(user_name, user_level, language, topic_title, topic_goal)
        else:
            logger.info(f"Final content quality score: {best_score:.2f}/1.0")
        
        return best_content
    
    def _generate_lesson_content(self, user_name: str, user_level: str, language: str, 
                                topic_title: str, topic_goal: str, iteration: int = 0, 
                                previous_feedback: str = "") -> str:
        """Generate comprehensive lesson content using AI with iterative improvement."""
        
        style = self.content_styles.get(user_level.lower(), self.content_styles["beginner"])
        sources = self.knowledge_sources.get(language, [])
        
        # Add iteration-specific improvements
        iteration_notes = ""
        if iteration > 0:
            iteration_notes = f"""
IMPROVEMENT NOTES (Iteration {iteration}):
- Previous feedback: {previous_feedback if previous_feedback else "First attempt"}
- Focus on improving clarity, accuracy, and engagement
- Ensure content is perfectly aligned with {user_level} level
"""
        
        prompt = f"""
You are a professional {language} programming tutor creating a lesson for {user_name}.

STUDENT INFORMATION:
- Name: {user_name}
- Skill Level: {user_level}
- Programming Language: {language.capitalize()}

LESSON TOPIC:
- Title: {topic_title}
- Learning Goal: {topic_goal}

TEACHING STYLE:
{style['tone']}
{style['complexity']}
{style['examples']}
{style['detail']}

{iteration_notes}

TASK: Create a comprehensive lesson that includes:

1. **Welcome and Introduction** - Greet {user_name} and introduce the topic
2. **Concept Explanation** - Explain {topic_title} in detail appropriate for {user_level} level
3. **Code Examples** - Provide 1 practical code example in {language}
4. **Step-by-step Breakdown** - Break down complex concepts into digestible parts
5. **Summary** - Recap what was learned

REQUIREMENTS:
- Use reliable sources: {', '.join(sources)}
- Match the user's skill level exactly
- Be encouraging and supportive
- Include practical, runnable code examples
- Make it engaging and interactive
- Keep the tone friendly and educational
- Ensure technical accuracy and correctness

OUTPUT FORMAT:
Create a well-structured lesson with clear sections, code example, and explanations.
Do not use JSON format - write it as a natural lesson text.

Generate a professional, educational lesson:
"""
        
        if not self.client:
            logger.error("No API client available. Please set OPENROUTER_API_KEY environment variable.")
            return self._create_fallback_lesson(user_name, user_level, language, topic_title, topic_goal)
            
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a programming education expert specializing in creating engaging lessons."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            return content.strip()
                
        except Exception as e:
            logger.error(f"Error generating lesson content: {e}")
            return self._create_fallback_lesson(user_name, user_level, language, topic_title, topic_goal)
    
    def _evaluate_content_quality(self, lesson_content: str, topic_title: str, topic_goal: str, 
                                 language: str, user_level: str) -> float:
        """Evaluate the quality of generated lesson content."""
        
        prompt = f"""
Evaluate this {language} programming lesson content for quality:

TOPIC: {topic_title}
LEARNING GOAL: {topic_goal}
USER SKILL LEVEL: {user_level}
CONTENT LENGTH: {len(lesson_content)} characters

CONTENT PREVIEW: {lesson_content[:500]}...

Rate the lesson content on a scale of 0.0 to 1.0 based on:

1. **Accuracy & Correctness (0.3 points)**
   - Is the technical information accurate?
   - Are code examples correct and runnable?

2. **Relevance & Alignment (0.25 points)**
   - Does it directly address the topic and learning goal?
   - Is it appropriate for the user's skill level?

3. **Clarity & Understandability (0.25 points)**
   - Is the explanation clear and easy to follow?
   - Are concepts broken down appropriately for the level?

4. **Engagement & Structure (0.2 points)**
   - Is the content well-structured and engaging?
   - Does it include practical examples and exercises?

Return only a number between 0.0 and 1.0:
"""
        
        if not self.client:
            logger.error("No API client available for evaluation. Using default score.")
            return 0.6
            
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a programming education evaluator specializing in lesson quality assessment."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.1
            )
            
            score_text = response.choices[0].message.content.strip()
            try:
                return float(score_text)
            except ValueError:
                return 0.6  # Default score
                
        except Exception as e:
            logger.error(f"Error evaluating content quality: {e}")
            return 0.6
    
    def _generate_improvement_feedback(self, lesson_content: str, score: float, 
                                     topic_title: str, user_level: str) -> str:
        """Generate specific feedback for improving lesson content in next iteration."""
        
        prompt = f"""
Analyze this {user_level} level programming lesson and provide specific improvement feedback.

TOPIC: {topic_title}
CURRENT SCORE: {score:.2f}/1.0
CONTENT LENGTH: {len(lesson_content)} characters

CONTENT PREVIEW: {lesson_content[:800]}...

Based on the score {score:.2f}, provide specific, actionable feedback to improve:

1. **If score < 0.7**: Focus on fundamental improvements (clarity, structure, accuracy)
2. **If score 0.7-0.8**: Focus on engagement and examples
3. **If score 0.8-0.85**: Fine-tune language and presentation

Provide 2-3 specific, actionable suggestions in 1-2 sentences total.
Focus on the most important improvements needed.

Example format: "Improve X by doing Y. Enhance Z with better examples."
"""
        
        if not self.client:
            logger.error("No API client available for feedback generation. Using default feedback.")
            return "Focus on improving clarity and adding more practical examples."
            
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a programming education expert providing improvement feedback."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            feedback = response.choices[0].message.content.strip()
            return feedback
                
        except Exception as e:
            logger.error(f"Error generating improvement feedback: {e}")
            return "Focus on improving clarity and adding more practical examples."
    
    def _create_fallback_lesson(self, user_name: str, user_level: str, language: str, 
                               topic_title: str, topic_goal: str) -> str:
        """Create fallback lesson if AI generation fails."""
        
        fallback_lesson = f"""
# Welcome to {language.capitalize()} Programming, {user_name}! 🎉

## Today's Topic: {topic_title}

**Learning Goal:** {topic_goal}

### What You'll Learn
In this lesson, you'll discover the fundamentals of {topic_title.lower()} in {language.capitalize()}. This is perfect for your {user_level} level!

### Key Concepts
- Basic understanding of {topic_title.lower()}
- Practical examples you can try
- Best practices for {language.capitalize()} programming

### Code Example
```{language}
// Basic {topic_title.lower()} example
// This will be covered in detail during the lesson
```

### Practice Exercise
Try to understand the concept and ask questions if anything is unclear!

### Next Steps
After this lesson, practice the concepts and move on to the next topic in your learning path.

---
*Note: This is a fallback lesson. The AI tutor will provide more detailed content in the next session.*
"""
        
        return fallback_lesson 