from src.models import EnvState

class TaskGrader:
    @staticmethod
    def evaluate(state: EnvState) -> float:
        """
        Returns a score between 0.0 and 1.0.
        """
        if not state.done:
            return 0.0
            
        score = 0.0
        
        if state.detected_shadow_ai:
            score += 0.5
            
        fp_penalty = state.false_positives * 0.2
        md_penalty = state.missed_detections * 0.2
        
        score -= fp_penalty
        score -= md_penalty
        
        return max(0.0, min(1.0, score + (0.5 if state.detected_shadow_ai else 0.0)))
        
class Tasks:
    EASY = {
        "id": "easy",
        "description": "Obvious Shadow AI usage. Focus on detecting direct calls to api.openai.com.",
        "success_criteria": "Correctly block/flag the usage within 5 steps without false positives."
    }
    MEDIUM = {
        "id": "medium",
        "description": "Subtle behavioral anomalies. High data transfer to unknown endpoints.",
        "success_criteria": "Recognize pattern over time and flag the anomalous endpoint."
    }
    HARD = {
        "id": "hard",
        "description": "Adversarial evasion. Low and slow data chunks.",
        "success_criteria": "Detect the shadow telemetry and block only the malicious activity."
    }
    
    @staticmethod
    def get_grader(task_id: str) -> TaskGrader:
        return TaskGrader()
