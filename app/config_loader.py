import os
from pathlib import Path
import yaml

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"


def load_yaml_file(filename: str) -> dict:
    path = CONFIG_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")
    with path.open("r", encoding="utf-8") as stream:
        return yaml.safe_load(stream) or {}


def load_agent_config(agent_type: str) -> dict:
    agents = load_yaml_file("agents.yaml")
    return agents.get(agent_type, {})


def load_task_config(task_type: str) -> dict:
    tasks = load_yaml_file("tasks.yaml")
    return tasks.get(task_type, {})
