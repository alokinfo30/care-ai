# app/agents.py
import os
import logging
from crewai import Agent
from app.config_loader import load_agent_config
from app.model_manager import model_manager

logger = logging.getLogger(__name__)

try:
    from crewai_tools import SerperDevTool, ScrapeWebsiteTool
    TOOLS_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ crewai_tools not available. Using fallback.")
    TOOLS_AVAILABLE = False

    class SerperDevTool:
        def __init__(self):
            self.name = "SerperDevTool"
            self.description = "Search tool (fallback)"

        def run(self, query):
            return f"Search results for: {query} (fallback)"

    class ScrapeWebsiteTool:
        def __init__(self):
            self.name = "ScrapeWebsiteTool"
            self.description = "Web scraping tool (fallback)"

        def run(self, url):
            return f"Scraped content from: {url} (fallback)"


def _build_agent(agent_key: str, default_role: str, default_goal: str, default_backstory: str, temperature: float, tools=None):
    config = load_agent_config(agent_key)
    model_config = model_manager.get_model_config(agent_key)
    llm = model_manager.get_llm(model_config["model"], model_config.get("temperature", temperature))

    return Agent(
        role=config.get("role", default_role),
        goal=config.get("goal", default_goal),
        backstory=config.get("backstory", default_backstory),
        allow_delegation=config.get("allow_delegation", False),
        verbose=config.get("verbose", True),
        llm=llm,
        tools=tools or [],
    )


def create_perception_agent():
    """Create the perception agent for sensor data analysis"""
    return _build_agent(
        "perception_agent",
        default_role="Sensor Data Analyst",
        default_goal="Analyze smartphone sensor data to understand user activity and environment",
        default_backstory=(
            "You are an AI perception specialist who interprets data from smartphone sensors. "
            "You analyze accelerometer, gyroscope, GPS, camera, and microphone data to "
            "understand what the user is doing and the surrounding context."
        ),
        temperature=0.2,
        tools=[SerperDevTool(), ScrapeWebsiteTool()] if TOOLS_AVAILABLE else [],
    )


def create_reasoning_agent():
    """Create the reasoning agent for context understanding"""
    return _build_agent(
        "reasoning_agent",
        default_role="Context & Reasoning Engine",
        default_goal="Understand user context and determine appropriate actions",
        default_backstory=(
            "You are an AI reasoning expert who understands human behavior patterns. "
            "You take sensor data and user context to determine what actions would be "
            "most helpful to the user, whether it's health monitoring, digital assistance, "
            "or proactive recommendations."
        ),
        temperature=0.4,
    )


def create_action_agent():
    """Create the action agent for task execution"""
    return _build_agent(
        "action_agent",
        default_role="Action Execution Specialist",
        default_goal="Execute appropriate actions through voice, notifications, and automation",
        default_backstory=(
            "You are an AI action specialist who converts decisions into executable actions. "
            "You can trigger voice responses, send notifications, automate tasks, and "
            "interact with other apps through intent systems."
        ),
        temperature=0.5,
    )


def create_context_agent():
    """Create the context memory agent"""
    return _build_agent(
        "context_agent",
        default_role="Context Memory Manager",
        default_goal="Maintain and manage user context, preferences, and history",
        default_backstory=(
            "You are an AI memory specialist who maintains user context, preferences, "
            "and historical data. You ensure the AI remembers user patterns and provides "
            "personalized experiences."
        ),
        temperature=0.3,
    )
