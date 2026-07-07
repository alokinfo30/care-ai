# app/tasks.py
from crewai import Task
from app.models import AgentAction
import yaml
import logging
import os

logger = logging.getLogger(__name__)

# Cache for task prompts to avoid repeated file I/O
_tasks_config_cache = None
_tasks_config_mtime = 0

def _load_task_prompts():
    """Load task prompts from the YAML config file, with caching."""
    global _tasks_config_cache, _tasks_config_mtime

    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'tasks.yaml')
    try:
        mtime = os.path.getmtime(config_path)
        # If file has been modified since last load, or cache is empty, reload.
        if mtime > _tasks_config_mtime or _tasks_config_cache is None:
            logger.info(f"Reloading tasks configuration from {config_path}.")
            with open(config_path, 'r') as file:
                _tasks_config_cache = yaml.safe_load(file)
            _tasks_config_mtime = mtime

        if _tasks_config_cache is None:
             raise ValueError("Task configuration cache is empty after attempting to load.")

        return _tasks_config_cache
    except (FileNotFoundError, yaml.YAMLError, ValueError) as e:
        logger.error(f"Failed to load or parse task config file at {config_path}: {e}")
        raise ValueError(f"Could not load tasks configuration from {config_path}") from e

def create_perceive_task(agent, sensor_data: str, language: str = "en"):
    """Create the perception task"""
    tasks_config = _load_task_prompts()
    config = tasks_config.get('perceive_task')
    if not config:
        raise ValueError("Configuration for 'perceive_task' not found in tasks.yaml")
    return Task(
        description=config.get('description', '').format(sensor_data=sensor_data, language=language),
        expected_output=config.get('expected_output', ''),
        agent=agent
    )

def create_reason_task(agent, history: str, language: str = "en"):
    """Create the reasoning task"""
    tasks_config = _load_task_prompts()
    config = tasks_config.get('reason_task')
    if not config:
        raise ValueError("Configuration for 'reason_task' not found in tasks.yaml")
    return Task(
        description=config.get('description', '').format(language=language, history=history),
        expected_output=config.get('expected_output', ''),
        agent=agent
    )

def create_action_task(agent, language: str = "en"):
    """Create the action task"""
    tasks_config = _load_task_prompts()
    config = tasks_config.get('action_task')
    if not config:
        raise ValueError("Configuration for 'action_task' not found in tasks.yaml")
    return Task(
        description=config.get('description', '').format(language=language),
        expected_output=config.get('expected_output', ''),
        agent=agent,
        output_pydantic=AgentAction
    )

def create_context_task(agent, user_id: str, language: str = "en"):
    """Create the context management task"""
    tasks_config = _load_task_prompts()
    config = tasks_config.get('context_task')
    if not config:
        raise ValueError("Configuration for 'context_task' not found in tasks.yaml")
    return Task(
        description=config.get('description', '').format(user_id=user_id, language=language),
        expected_output=config.get('expected_output', ''),
        agent=agent
    )