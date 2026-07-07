# app/models.py
from pydantic import BaseModel, Field
from typing import Dict, Optional, List, Any
from datetime import datetime
from enum import Enum

class ActivityType(str, Enum):
    """User activity types"""
    WALKING = "walking"
    DRIVING = "driving"
    SITTING = "sitting"
    SLEEPING = "sleeping"
    RUNNING = "running"
    CYCLING = "cycling"
    UNKNOWN = "unknown"

class SensorData(BaseModel):
    """Smartphone sensor data"""
    accelerometer: Dict[str, float] = Field(..., description="Accelerometer readings")
    gyroscope: Dict[str, float] = Field(..., description="Gyroscope readings")
    location: Dict[str, float] = Field(..., description="GPS location")
    audio_level: float = Field(..., description="Ambient audio level")
    light_level: float = Field(..., description="Ambient light level")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class UserContext(BaseModel):
    """User context and activity"""
    user_id: str = Field(..., description="User identifier")
    activity: ActivityType = Field(..., description="Current activity")
    location: str = Field(..., description="Location description")
    time_of_day: str = Field(..., description="Time of day")
    mood: Optional[str] = Field(None, description="Detected mood")
    energy_level: int = Field(..., ge=1, le=10, description="Energy level 1-10")
    health_indicators: Dict[str, Any] = Field(..., description="Health metrics")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class Action(BaseModel):
    """Action to execute"""
    id: str = Field(..., description="Action identifier")
    type: str = Field(..., description="Action type: voice, notification, automation, alert")
    priority: str = Field(..., description="Priority: low, medium, high, critical")
    content: str = Field(..., description="Action content")
    method: str = Field(..., description="Execution method")
    status: str = Field("pending", description="Action status")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class HealthAlert(BaseModel):
    """Health alert"""
    type: str = Field(..., description="Alert type: fall, activity_overload, sleep_deprivation")
    severity: str = Field(..., description="Severity: low, medium, high")
    message: str = Field(..., description="Alert message")
    action_required: str = Field(..., description="Required action")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class UserMemory(BaseModel):
    """User memory and preferences"""
    user_id: str = Field(..., description="User identifier")
    daily_routine: Dict[str, Any] = Field(..., description="Daily routine patterns")
    preferences: Dict[str, Any] = Field(..., description="User preferences")
    health_history: List[Dict] = Field(..., description="Health history")
    task_history: List[Dict] = Field(..., description="Task completion history")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class RobotResponse(BaseModel):
    """Complete robot response"""
    context: UserContext = Field(..., description="User context")
    actions: List[Action] = Field(..., description="Actions to execute")
    alerts: List[HealthAlert] = Field(..., description="Health alerts")
    memory: UserMemory = Field(..., description="Updated memory")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())