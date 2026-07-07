# app/agents.py
import os
import logging
from crewai import Agent
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

def create_perception_agent():
    """Create the perception agent for sensor data analysis"""
    config = model_manager.get_model_config('perception_agent')
    llm = model_manager.get_llm(config['model'], config.get('temperature', 0.2))
    
    return Agent(
        role="Sensor Data Analyst",
        goal="Analyze smartphone sensor data to understand user activity and environment",
        backstory=(
            "You are an AI perception specialist who interprets data from smartphone sensors. "
            "You analyze accelerometer, gyroscope, GPS, camera, and microphone data to "
            "understand what the user is doing and the surrounding context."
        ),
        allow_delegation=False,
        verbose=True,
        llm=llm,
        tools=[SerperDevTool(), ScrapeWebsiteTool()]
    )

def create_reasoning_agent():
    """Create the reasoning agent for context understanding"""
    config = model_manager.get_model_config('reasoning_agent')
    llm = model_manager.get_llm(config['model'], config.get('temperature', 0.4))
    
    return Agent(
        role="Context & Reasoning Engine",
        goal="Understand user context and determine appropriate actions",
        backstory=(
            "You are an AI reasoning expert who understands human behavior patterns. "
            "You take sensor data and user context to determine what actions would be "
            "most helpful to the user, whether it's health monitoring, digital assistance, "
            "or proactive recommendations."
        ),
        allow_delegation=False,
        verbose=True,
        llm=llm
    )

def create_action_agent():
    """Create the action agent for task execution"""
    config = model_manager.get_model_config('action_agent')
    llm = model_manager.get_llm(config['model'], config.get('temperature', 0.5))
    
    return Agent(
        role="Action Execution Specialist",
        goal="Execute appropriate actions through voice, notifications, and automation",
        backstory=(
            "You are an AI action specialist who converts decisions into executable actions. "
            "You can trigger voice responses, send notifications, automate tasks, and "
            "interact with other apps through intent systems."
        ),
        allow_delegation=False,
        verbose=True,
        llm=llm
    )

def create_context_agent():
    """Create the context memory agent"""
    config = model_manager.get_model_config('context_agent')
    llm = model_manager.get_llm(config['model'], config.get('temperature', 0.3))
    
    return Agent(
        role="Context Memory Manager",
        goal="Maintain and manage user context, preferences, and history",
        backstory=(
            "You are an AI memory specialist who maintains user context, preferences, "
            "and historical data. You ensure the AI remembers user patterns and provides "
            "personalized experiences."
        ),
        allow_delegation=False,
        verbose=True,
        llm=llm
    )