# app/crew.py
from crewai import Crew
import os
import logging
from typing import Dict, List, Optional
from app.model_manager import model_manager
from app.models import AgentAction
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

            # 1. Create Agents
            perception_agent = self.create_perception_agent()
            reasoning_agent = self.create_reasoning_agent()
            action_agent = self.create_action_agent()
            context_agent = self.create_context_agent()

            # 2. Create Tasks
            perceive_task = self.create_perceive_task(perception_agent, sensor_data, language)
            reason_task = self.create_reason_task(reasoning_agent, "User history", language)
            action_task = self.create_action_task(action_agent, language)
            context_task = self.create_context_task(context_agent, user_id, language)

            # 3. Create a single Crew to run the sequential process
            crew = Crew(
                agents=[perception_agent, reasoning_agent, action_agent, context_agent],
                tasks=[perceive_task, reason_task, action_task, context_task],
                verbose=self.verbose
            )

            # 4. Kick off the crew. The output of the last task is returned.
            crew.kickoff()

            # 5. Correctly serialize the Pydantic output from the action_task
            action_output = action_task.output
            if isinstance(action_output, AgentAction):
                action_json_str = action_output.model_dump_json()
            else:
                action_json_str = str(action_output)

            return {
                "status": "success",
                "user_id": user_id,
                "perception": str(perceive_task.output),
                "reasoning": str(reason_task.output),
                "actions": action_json_str,
                "context": str(context_task.output),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Processing failed: {str(e)}")
            return {
                "status": "error",
                "user_id": user_id,
                "error": str(e)
            }