from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class APIEvent(BaseModel):
    timestamp: float
    user_id: str
    endpoint: str
    bytes_transferred: int
    is_suspicious: bool = False

class Observation(BaseModel):
    current_step: int
    recent_events: List[APIEvent]
    radar_anomaly_score: float
    historical_risk_score: float
    user_behavior_summaries: Dict[str, str]
    system_load: float

class Action(BaseModel):
    decision: str = Field(..., description="Must be one of: 'allow', 'flag', 'monitor', 'block', 'increase_risk_score'")
    target_user: Optional[str] = Field(None, description="The user to apply the decision to")
    reasoning: Optional[str] = Field(None, description="Explanation for the action")

class Reward(BaseModel):
    value: float
    reason: str

class EnvState(BaseModel):
    step_count: int
    max_steps: int
    task_id: str
    total_reward: float
    done: bool
    users: List[str]
    detected_shadow_ai: bool
    false_positives: int
    missed_detections: int
    current_risk_scores: Dict[str, float]
    api_history: List[APIEvent]
