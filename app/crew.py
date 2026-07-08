from crewai import Crew
import os
import logging
from typing import Dict, Any
from app.models import AgentAction
from app.context_store import UserMemoryStore
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
                create_context_agent,
            )
            from app.tasks import (
                create_perceive_task,
                create_reason_task,
                create_action_task,
                create_context_task,
            )

            self.create_perception_agent = create_perception_agent
            self.create_reasoning_agent = create_reasoning_agent
            self.create_action_agent = create_action_agent
            self.create_context_agent = create_context_agent

            self.create_perceive_task = create_perceive_task
            self.create_reason_task = create_reason_task
            self.create_action_task = create_action_task
            self.create_context_task = create_context_task

            self.verbose = os.getenv("DEBUG", "False").lower() == "true"
            self.memory_store = UserMemoryStore()

            logger.info("✅ SmartphoneRobotCrew initialized")
        except Exception as e:
            logger.error(f"Failed to initialize SmartphoneRobotCrew: {e}")
            raise

    def _extract_output(self, crew_output: Any) -> str:
        if crew_output is None:
            return ""
        if hasattr(crew_output, "raw") and crew_output.raw:
            return str(crew_output.raw)
        if hasattr(crew_output, "json_dict") and crew_output.json_dict:
            return str(crew_output.json_dict)
        if hasattr(crew_output, "pydantic") and crew_output.pydantic is not None:
            return str(crew_output.pydantic)
        return str(crew_output)

    def _task_output(self, task_obj: Any) -> Any:
        if task_obj is None:
            return None
        if hasattr(task_obj, "output") and task_obj.output is not None:
            return task_obj.output
        if hasattr(task_obj, "json_dict") and task_obj.json_dict is not None:
            return task_obj.json_dict
        if hasattr(task_obj, "raw"):
            return task_obj.raw
        return None

    def process_sensor_data(self, sensor_data: str, user_id: str, language: str = "en") -> Dict[str, Any]:
        """Process sensor data and generate actions"""
        try:
            logger.info(f"📱 Processing sensor data for user {user_id}")

            user_history = self.memory_store.get_history_summary(user_id)

            perception_agent = self.create_perception_agent()
            perceive_task = self.create_perceive_task(perception_agent, sensor_data, language)
            perception_crew = Crew(agents=[perception_agent], tasks=[perceive_task], verbose=self.verbose)
            perception_result = perception_crew.kickoff({
                "sensor_data": sensor_data,
                "language": language,
            })
            perception_text = self._extract_output(perception_result)

            reasoning_agent = self.create_reasoning_agent()
            reason_task = self.create_reason_task(reasoning_agent, perception_text, user_history, language)
            reasoning_crew = Crew(agents=[reasoning_agent], tasks=[reason_task], verbose=self.verbose)
            reasoning_result = reasoning_crew.kickoff({
                "analysis": perception_text,
                "history": user_history,
                "language": language,
            })
            reasoning_text = self._extract_output(reasoning_result)

            action_agent = self.create_action_agent()
            action_task = self.create_action_task(action_agent, reasoning_text, language)
            action_crew = Crew(agents=[action_agent], tasks=[action_task], verbose=self.verbose)
            action_result = action_crew.kickoff({
                "reasoning": reasoning_text,
                "language": language,
            })
            action_text = self._extract_output(action_result)
            action_output = self._task_output(action_task)

            context_agent = self.create_context_agent()
            context_task = self.create_context_task(context_agent, action_text, user_id, language)
            context_crew = Crew(agents=[context_agent], tasks=[context_task], verbose=self.verbose)
            context_result = context_crew.kickoff({
                "new_data": action_text,
                "user_id": user_id,
                "language": language,
            })
            context_text = self._extract_output(context_result)

            if isinstance(action_output, AgentAction):
                action_serialized = action_output.model_dump()
            else:
                action_serialized = action_output

            summary_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "summary": str(action_text),
                "actions": action_serialized,
            }
            updated_memory = self.memory_store.update_user_memory(
                user_id,
                {
                    "task_history": summary_entry,
                    "health_history": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "notes": "Processed sensor event",
                    },
                },
            )

            return {
                "status": "success",
                "user_id": user_id,
                "perception": perception_text,
                "reasoning": reasoning_text,
                "actions": action_serialized,
                "context": context_text,
                "memory": updated_memory,
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.exception(f"Processing failed: {e}")
            return {
                "status": "error",
                "user_id": user_id,
                "error": str(e),
            }
