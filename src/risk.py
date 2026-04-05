class SafeRiskModel:
    def __init__(self):
        self.global_risk_score = 0.0
        self.decay_rate = 0.9
    
    def update(self, anomaly_score: float) -> float:
        """
        Aggregates anomaly signals into a normalized risk score (0-1).
        """
        if anomaly_score > 0.3:
            increase = anomaly_score * 0.5
            self.global_risk_score = min(1.0, self.global_risk_score + increase)
        else:
            self.global_risk_score *= self.decay_rate
            
        return float(self.global_risk_score)
