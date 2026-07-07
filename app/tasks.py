# app/tasks.py
from crewai import Task
import logging

logger = logging.getLogger(__name__)

def create_perceive_task(agent, sensor_data: str, language: str = "en"):
    """Create the perception task"""
    return Task(
        description=f"""
        Analyze the following smartphone sensor data:
        
        Sensor Data:
        {sensor_data}
        
        Analyze:
        1. User activity (walking, driving, sitting, sleeping)
        2. Location context (home, office, outdoors, vehicle)
        3. Time context (morning, afternoon, evening, night)
        4. Environmental factors (noise level, light level)
        5. Health indicators (steps, activity duration, posture)
        
        Language: {language}
        """,
        expected_output="""
        A comprehensive analysis of user context and activity with clear classification.
        """,
        agent=agent
    )

def create_reason_task(agent, analysis: str, history: str, language: str = "en"):
    """Create the reasoning task"""
    return Task(
        description=f"""
        Based on the sensor analysis, reason about user needs:
        
        Analysis Results:
        {analysis}
        
        User History:
        {history}
        
        Determine:
        1. What is the user's current activity and context?
        2. Compare the current activity with the user's historical patterns for this time of day.
        3. Is there a deviation from the user's normal routine (e.g., a delay in morning activity)?
        4. Identify potential needs, risks, or opportunities for assistance.
        5. If a deviation is detected, formulate a gentle, helpful reminder.
        6. If a health or safety risk is identified (like a fall), formulate a critical alert.
        7. Suggest one proactive action that would be helpful.
        
        Language: {language}
        """,
        expected_output="""
        A reasoned assessment of the user's situation, including any detected routine deviations and specific, prioritized recommendations for actions (e.g., reminders, alerts, or suggestions).
        """,
        agent=agent
    )

def create_action_task(agent, reasoning: str, language: str = "en"):
    """Create the action task"""
    return Task(
        description=f"""
        Based on the reasoning, execute appropriate actions:
        
        Reasoning Results:
        {reasoning}
        
        Actions to consider:
        1. **voice_reminder**: A spoken reminder about a routine deviation.
        2. **critical_alert**: A spoken, urgent alert for safety issues (e.g., a fall).
        3. **voice_suggestion**: A helpful, proactive spoken suggestion.
        4. **notification**: A standard, non-spoken on-screen notification.
        
        Based on the reasoning, formulate the single most important action to take.
        If the reasoning mentions a "critical alert", you MUST generate a 'critical_alert' action.
        If it mentions a "reminder", generate a 'voice_reminder' action.
        Language: {language}
        """,
        expected_output="""
        A single, specific, and executable action in a structured format, including the type (e.g., 'voice_reminder') and the exact content to be spoken or displayed.
        """,
        agent=agent
    )

def create_context_task(agent, new_data: str, user_id: str, language: str = "en"):
    """Create the context management task"""
    return Task(
        description=f"""
        Update user context and memory:
        
        New Data:
        {new_data}
        
        User ID: {user_id}
        
        Update:
        1. Activity history
        2. Health metrics
        3. Task completion status
        4. Preferences and patterns
        5. Long-term memory
        
        Language: {language}
        """,
        expected_output="""
        Updated context store with new information and insights.
        """,
        agent=agent
    )