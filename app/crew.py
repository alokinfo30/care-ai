# app/crew.py
from crewai import Crew
import os
import logging
from typing import Dict, List, Optional
from app.model_manager import model_manager
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class SmartphoneRobotCrew:
    """Orchestrate the Smartphone Robot assistant services"""
    
    def __init__(self):
        try:
            from app.agents import (
                create_perception_agent,
                create_reasoning_agent,
                create_action_agent,
                create_context_agent
            )
            from app.tasks import (
                create_perceive_task,
                create_reason_task,
                create_action_task,
                create_context_task
            )
            
            self.create_perception_agent = create_perception_agent
            self.create_reasoning_agent = create_reasoning_agent
            self.create_action_agent = create_action_agent
            self.create_context_agent = create_context_agent
            
            self.create_perceive_task = create_perceive_task
            self.create_reason_task = create_reason_task
            self.create_action_task = create_action_task
            self.create_context_task = create_context_task
            
            self.verbose = os.getenv('DEBUG', 'False').lower() == 'true'
            self.model_manager = model_manager
            
            logger.info("✅ SmartphoneRobotCrew initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize SmartphoneRobotCrew: {str(e)}")
            raise
    
    def process_sensor_data(self, sensor_data: str, user_id: str, language: str = "en") -> Dict:
        """Process sensor data and generate actions"""
        try:
            logger.info(f"📱 Processing sensor data for user {user_id}")
            
            # Step 1: Perception
            perception_agent = self.create_perception_agent()
            perceive_task = self.create_perceive_task(perception_agent, sensor_data, language)
            perceive_crew = Crew(agents=[perception_agent], tasks=[perceive_task], verbose=self.verbose)
            perception_result = perceive_crew.kickoff(inputs={
                "sensor_data": sensor_data,
                "language": language
            })
            
            # Step 2: Reasoning
            reasoning_agent = self.create_reasoning_agent()
            reason_task = self.create_reason_task(reasoning_agent, str(perception_result), "User history", language)
            reason_crew = Crew(agents=[reasoning_agent], tasks=[reason_task], verbose=self.verbose)
            reasoning_result = reason_crew.kickoff(inputs={
                "analysis": str(perception_result),
                "history": "User history",
                "language": language
            })
            
            # Step 3: Action
            action_agent = self.create_action_agent()
            action_task = self.create_action_task(action_agent, str(reasoning_result), language)
            action_crew = Crew(agents=[action_agent], tasks=[action_task], verbose=self.verbose)
            action_result = action_crew.kickoff(inputs={
                "reasoning": str(reasoning_result),
                "language": language
            })
            
            # Step 4: Context Update
            context_agent = self.create_context_agent()
            context_task = self.create_context_task(context_agent, str(action_result), user_id, language)
            context_crew = Crew(agents=[context_agent], tasks=[context_task], verbose=self.verbose)
            context_result = context_crew.kickoff(inputs={
                "new_data": str(action_result),
                "user_id": user_id,
                "language": language
            })
            
            return {
                "status": "success",
                "user_id": user_id,
                "perception": str(perception_result),
                "reasoning": str(reasoning_result),
                "actions": str(action_result),
                "context": str(context_result),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Processing failed: {str(e)}")
            return {
                "status": "error",
                "user_id": user_id,
                "error": str(e)
            }