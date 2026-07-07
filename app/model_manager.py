# app/model_manager.py
import os
import logging
import random
from typing import List, Dict, Optional, Any
from enum import Enum
import time
from openai import OpenAI
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)

class FallbackStrategy(Enum):
    SEQUENTIAL = "sequential"
    RANDOM = "random"
    ROUND_ROBIN = "round_robin"

class ModelManager:
    """Manages multiple models with fallback support for Smartphone Robot"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables!")
        
        self.base_url = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
        self.app_url = os.getenv('OPENROUTER_APP_URL', 'http://localhost:5000')
        self.app_name = os.getenv('OPENROUTER_APP_NAME', 'SmartphoneRobot')
        
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            default_headers={
                "HTTP-Referer": self.app_url,
                "X-Title": self.app_name
            }
        )
        
        self.primary_model = os.getenv('OPENROUTER_PRIMARY_MODEL', 'openai/gpt-4o-mini')
        self.fallback_models = self._get_fallback_models()
        
        self.agent_models = {
            'perception_agent': os.getenv('PERCEPTION_MODEL', self.primary_model),
            'reasoning_agent': os.getenv('REASONING_MODEL', self.primary_model),
            'action_agent': os.getenv('ACTION_MODEL', self.primary_model),
            'context_agent': os.getenv('CONTEXT_MODEL', self.primary_model)
        }
        
        strategy_name = os.getenv('MODEL_FALLBACK_STRATEGY', 'sequential')
        try:
            self.strategy = FallbackStrategy(strategy_name.lower())
        except ValueError:
            self.strategy = FallbackStrategy.SEQUENTIAL
        
        self._round_robin_counter = 0
        self._model_cache = {}
        self._last_test_time = 0
        self._cache_duration = 300
        
        logger.info(f"🚀 Model Manager initialized for Smartphone Robot")
        logger.info(f"  Primary Model: {self.primary_model}")
        logger.info(f"  Fallback Models: {self.fallback_models}")
        logger.info(f"  Strategy: {self.strategy.value}")
    
    def _get_fallback_models(self) -> List[str]:
        fallbacks = os.getenv('OPENROUTER_FALLBACK_MODELS', '')
        if fallbacks:
            return [m.strip() for m in fallbacks.split(',')]
        return [
            "mistralai/mixtral-8x22b-instruct",
            "meta-llama/llama-3.1-8b-instruct",
            "deepseek/deepseek-chat"
        ]
    
    def get_available_models(self) -> List[str]:
        current_time = time.time()
        if current_time - self._last_test_time < self._cache_duration:
            if self._model_cache:
                return self._model_cache
        
        all_models = [self.primary_model] + self.fallback_models
        available = []
        for model in all_models:
            if self._test_model(model):
                available.append(model)
        
        self._model_cache = available
        self._last_test_time = current_time
        return available
    
    def _test_model(self, model: str) -> bool:
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5,
                timeout=10
            )
            return True
        except Exception as e:
            logger.debug(f"Model {model} unavailable: {str(e)}")
            return False
    
    def get_next_model(self, preferred: Optional[str] = None) -> str:
        available = self.get_available_models()
        if not available:
            logger.warning("No available models, using primary model")
            return self.primary_model
        
        if preferred and preferred in available:
            return preferred
        
        if self.strategy == FallbackStrategy.SEQUENTIAL:
            return available[0]
        elif self.strategy == FallbackStrategy.RANDOM:
            return random.choice(available)
        elif self.strategy == FallbackStrategy.ROUND_ROBIN:
            model = available[self._round_robin_counter % len(available)]
            self._round_robin_counter += 1
            return model
        else:
            return available[0]
    
    def get_model_config(self, agent_type: str) -> Dict[str, Any]:
        preferred = self.agent_models.get(agent_type, self.primary_model)
        chosen_model = self.get_next_model(preferred)
        logger.info(f"Agent {agent_type} using model: {chosen_model}")
        
        return {
            'model': chosen_model,
            'temperature': self._get_agent_temperature(agent_type)
        }
    
    def _get_agent_temperature(self, agent_type: str) -> float:
        temperatures = {
            'perception_agent': 0.2,
            'reasoning_agent': 0.4,
            'action_agent': 0.5,
            'context_agent': 0.3
        }
        return temperatures.get(agent_type, 0.3)
    
    def get_llm(self, model: str, temperature: float = 0.3):
        try:
            return ChatOpenAI(
                model=model,
                api_key=self.api_key,
                base_url=self.base_url,
                temperature=temperature,
                default_headers={
                    "HTTP-Referer": self.app_url,
                    "X-Title": self.app_name
                }
            )
        except Exception as e:
            logger.error(f"Error creating LLM: {str(e)}")
            return None
    
    def test_providers(self) -> Dict[str, bool]:
        results = {}
        all_models = [self.primary_model] + self.fallback_models
        for model in all_models:
            try:
                logger.info(f"Testing {model}...")
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": "Say OK"}],
                    max_tokens=10
                )
                results[model] = True
                logger.info(f"✅ {model} is available")
            except Exception as e:
                results[model] = False
                logger.warning(f"❌ {model} unavailable: {str(e)}")
        return results

model_manager = ModelManager()