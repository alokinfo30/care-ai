import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / 'data'
DATA_DIR.mkdir(exist_ok=True)
LOCAL_STORE = DATA_DIR / 'user_memory.json'


class UserMemoryStore:
    def __init__(self):
        self.redis_url = os.getenv('REDIS_URL')
        self.redis = None
        if self.redis_url:
            try:
                from redis import Redis
                self.redis = Redis.from_url(self.redis_url)
            except Exception as exc:
                logger.warning(f"Redis unavailable, falling back to local store: {exc}")
                self.redis = None

    def _load_local(self) -> Dict[str, Any]:
        if not LOCAL_STORE.exists():
            return {}
        try:
            with LOCAL_STORE.open('r', encoding='utf-8') as fh:
                return json.load(fh)
        except json.JSONDecodeError:
            return {}

    def _save_local(self, payload: Dict[str, Any]):
        with LOCAL_STORE.open('w', encoding='utf-8') as fh:
            json.dump(payload, fh, indent=2)

    def _user_key(self, user_id: str) -> str:
        return f"user_memory:{user_id}"

    def get_user_memory(self, user_id: str) -> Dict[str, Any]:
        if self.redis:
            raw = self.redis.get(self._user_key(user_id))
            if raw:
                try:
                    return json.loads(raw)
                except json.JSONDecodeError:
                    return {}
            return {}

        data = self._load_local()
        return data.get(user_id, {})

    def save_user_memory(self, user_id: str, memory: Dict[str, Any]):
        if self.redis:
            self.redis.set(self._user_key(user_id), json.dumps(memory))
            return

        data = self._load_local()
        data[user_id] = memory
        self._save_local(data)

    def get_history_summary(self, user_id: str) -> str:
        memory = self.get_user_memory(user_id)
        history = memory.get('task_history', [])
        if not history:
            return 'No prior history.'
        lines = []
        for item in history[-5:]:
            timestamp = item.get('timestamp', 'unknown')
            summary = item.get('summary', item.get('actions', 'no summary'))
            lines.append(f"{timestamp}: {summary}")
        return '\n'.join(lines)

    def update_user_memory(self, user_id: str, update: Dict[str, Any]):
        memory = self.get_user_memory(user_id)
        memory.setdefault('user_id', user_id)
        memory.setdefault('daily_routine', {})
        memory.setdefault('preferences', {})
        memory.setdefault('health_history', [])
        memory.setdefault('task_history', [])

        if 'preferences' in update:
            memory['preferences'].update(update['preferences'])

        if 'health_history' in update:
            memory['health_history'].append(update['health_history'])

        if 'task_history' in update:
            memory['task_history'].append(update['task_history'])

        memory['updated_at'] = datetime.utcnow().isoformat()
        self.save_user_memory(user_id, memory)
        return memory
