import numpy as np
from typing import List, Dict
from src.models import APIEvent

class RadarAnomalyDetector:
    def __init__(self):
        self.history: Dict[str, List[Dict[str, float]]] = {}

    def analyze(self, events: List[APIEvent]) -> float:
        """
        Returns a radar anomaly score between 0.0 and 1.0 based on recent events.
        """
        if not events:
            return 0.0
            
        axes_scores = []
        
        # Axis 1: Volume Anomaly
        total_bytes = sum(e.bytes_transferred for e in events)
        if total_bytes > 50000:
            axes_scores.append(min((total_bytes - 50000) / 100000.0, 1.0))
        else:
            axes_scores.append(0.0)
            
        # Axis 2: Suspicious Endpoint Anomaly
        suspicious_calls = sum(1 for e in events if "api.openai.com" in e.endpoint or "claude.ai" in e.endpoint or e.is_suspicious)
        if len(events) > 0:
            susp_ratio = suspicious_calls / len(events)
            axes_scores.append(susp_ratio)
        else:
            axes_scores.append(0.0)
            
        # Axis 3: Frequency Anomaly
        freq_score = min(len(events) / 20.0, 1.0)
        axes_scores.append(freq_score)
        
        axes_scores.sort(reverse=True)
        radar_score = np.mean(axes_scores[:2])
        
        return float(radar_score)
