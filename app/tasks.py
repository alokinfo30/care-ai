from crewai import Task
from app.models import AgentAction
from app.config_loader import load_task_config
import logging

logger = logging.getLogger(__name__)

def create_perceive_task(agent, sensor_data: str, language: str = "en"):
    """Create the perception task"""
    config = load_task_config('perceive_task')
    return Task(
        description=config.get('description', '').format(sensor_data=sensor_data, language=language),
        expected_output=config.get('expected_output', ''),
        agent=agent
    )

def create_reason_task(agent, analysis: str, history: str, language: str = "en"):
    """Create the reasoning task"""
    config = load_task_config('reason_task')
    return Task(
        description=config.get('description', '').format(analysis=analysis, history=history, language=language),
        expected_output=config.get('expected_output', ''),
        agent=agent
    )

def create_action_task(agent, reasoning: str, language: str = "en"):
    """Create the action task"""
    config = load_task_config('action_task')
    return Task(
        description=config.get('description', '').format(reasoning=reasoning, language=language),
        expected_output=config.get('expected_output', ''),
        agent=agent,
        output_pydantic=AgentAction
    )

def create_context_task(agent, new_data: str, user_id: str, language: str = "en"):
    """Create the context management task"""
    config = load_task_config('context_task')
    return Task(
        description=config.get('description', '').format(context=new_data, user_id=user_id, language=language),
        expected_output=config.get('expected_output', ''),
        agent=agent
    )
