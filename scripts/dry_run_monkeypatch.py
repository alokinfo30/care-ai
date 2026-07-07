#!/usr/bin/env python3
"""Dry-run script: monkeypatch Crew.kickoff to validate SmartphoneRobotCrew workflow
This avoids external LLM and Redis dependencies and verifies parsing/serialization.
"""
import sys
import os

# Ensure project root is on sys.path so `app` package imports resolve
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from crewai import Crew
from app.crew import SmartphoneRobotCrew
from app.models import AgentAction
from app.model_manager import model_manager

# Monkeypatch model_manager.get_llm to return a simple model name (avoids validation issues)
model_manager.get_llm = lambda model, temperature=0.3: model

# Replace agent factory functions with lightweight stubs to avoid LLM initialization
import app.agents as agents_mod
agents_mod.create_perception_agent = lambda: "perception_agent_stub"
agents_mod.create_reasoning_agent = lambda: "reasoning_agent_stub"
agents_mod.create_action_agent = lambda: "action_agent_stub"
agents_mod.create_context_agent = lambda: "context_agent_stub"

# Stub task factories so they don't construct real crewai.Task objects
import app.tasks as tasks_mod
tasks_mod.create_perceive_task = lambda agent, sensor_data, language='en': {'descr': 'perceive_stub'}
tasks_mod.create_reason_task = lambda agent, analysis, history, language='en': {'descr': 'reason_stub'}
tasks_mod.create_action_task = lambda agent, reasoning, language='en': {'descr': 'action_stub'}
tasks_mod.create_context_task = lambda agent, new_data, user_id, language='en': {'descr': 'context_stub'}

# Replace Crew inside app.crew with a lightweight FakeCrew that uses our fake kickoff
import app.crew as crew_mod

class FakeCrew:
    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs

    def kickoff(self, inputs=None, input_files=None, from_checkpoint=None):
        return _fake_kickoff(self, inputs, input_files, from_checkpoint)

crew_mod.Crew = FakeCrew

# Backup original kickoff
_orig_kickoff = Crew.kickoff

class FakeOutput:
    def __init__(self, raw=None, json_dict=None, pydantic=None):
        self.raw = raw
        self.json_dict = json_dict
        self.pydantic = pydantic


def _fake_kickoff(self, inputs=None, input_files=None, from_checkpoint=None):
    # Determine stage by input keys
    if inputs and 'sensor_data' in inputs:
        return FakeOutput(raw="User is walking outdoors; noisy environment")
    if inputs and 'analysis' in inputs:
        return FakeOutput(raw="Detected routine deviation: suggest reminder")
    if inputs and 'reasoning' in inputs:
        # Return a pydantic AgentAction to test serialization path
        action = AgentAction(type="voice_reminder", content="It's time for your walk.")
        return FakeOutput(pydantic=action)
    if inputs and 'new_data' in inputs:
        return FakeOutput(raw="Memory updated successfully")
    return FakeOutput(raw="fallback")

# Apply monkeypatch
Crew.kickoff = _fake_kickoff

try:
    crew = SmartphoneRobotCrew()
    result = crew.process_sensor_data("accel:0.1,0.2;gyro:0.0;gps:loc", "dryrun-user")
    print('Dry-run result:')
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))
finally:
    # Restore original
    Crew.kickoff = _orig_kickoff
