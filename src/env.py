from typing import Dict, Any, Tuple
from src.models import Observation, Action, Reward, EnvState
from src.simulation import Simulator
from src.anomaly import RadarAnomalyDetector
from src.risk import SafeRiskModel

class ShadowAIEnv:
    def __init__(self):
        self.max_steps = 20
        self.reset("easy")
        
    def reset(self, task_id: str = "easy") -> Observation:
        self.task_id = task_id
        self.simulator = Simulator(task_id)
        self.anomaly_detector = RadarAnomalyDetector()
        self.risk_model = SafeRiskModel()
        
        self.state_data = EnvState(
            step_count=0,
            max_steps=self.max_steps,
            task_id=task_id,
            total_reward=0.0,
            done=False,
            users=["alice_dev", "bob_finance", "charlie_ops", "dave_sales"],
            detected_shadow_ai=False,
            false_positives=0,
            missed_detections=0,
            current_risk_scores={},
            api_history=[]
        )
        
        events = self.simulator.generate_events(0)
        self.state_data.api_history.extend(events)
        
        return self._get_observation(events)
        
    def _get_observation(self, recent_events) -> Observation:
        anomaly_score = self.anomaly_detector.analyze(recent_events)
        risk_score = self.risk_model.update(anomaly_score)
        
        return Observation(
            current_step=self.state_data.step_count,
            recent_events=recent_events,
            radar_anomaly_score=anomaly_score,
            historical_risk_score=risk_score,
            user_behavior_summaries={u: "Normal" for u in self.state_data.users},
            system_load=0.45
        )
        
    def step(self, action: Action) -> Tuple[Observation, Reward, bool, Dict[str, Any]]:
        self.state_data.step_count += 1
        
        events = self.simulator.generate_events(self.state_data.step_count)
        self.state_data.api_history.extend(events)
        
        reward_val = 0.0
        reason = ""
        
        has_shadow_ai = any(e.is_suspicious for e in events)
        
        if action.decision in ["flag", "block"]:
            if has_shadow_ai:
                reward_val = 1.0
                reason = "Correctly detected Shadow AI."
                self.state_data.detected_shadow_ai = True
            else:
                reward_val = -0.5
                reason = "False positive. Disrupted normal operations."
                self.state_data.false_positives += 1
        elif action.decision in ["allow", "monitor", "increase_risk_score"]:
            if has_shadow_ai:
                reward_val = -1.0
                reason = "Missed Shadow AI usage."
                self.state_data.missed_detections += 1
            else:
                reward_val = +0.1
                reason = "Correctly handled normal traffic."
                
        self.state_data.total_reward += reward_val
        
        if self.state_data.step_count >= self.max_steps or self.state_data.detected_shadow_ai:
            self.state_data.done = True
            
        obs = self._get_observation(events)
        reward = Reward(value=reward_val, reason=reason)
        
        info = {"total_reward": self.state_data.total_reward}
        
        return obs, reward, self.state_data.done, info
        
    def state(self) -> EnvState:
        return self.state_data
