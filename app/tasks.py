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
        1. What is the user doing?
        2. What potential needs or risks exist?
        3. What proactive actions would be helpful?
        4. What health or safety concerns should be addressed?
        5. What digital tasks could be automated?
        
        Language: {language}
        """,
        expected_output="""
        A reasoned assessment of user needs with recommended actions.
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
        1. Voice responses and alerts
        2. Notifications and reminders
        3. Task automation (bills, bookings, emails)
        4. Health and safety alerts
        5. Proactive suggestions
        
        Prioritize actions based on urgency and importance.
        Language: {language}
        """,
        expected_output="""
        A list of prioritized actions to execute with execution methods.
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