import random
import time
from typing import List, Dict
from src.models import APIEvent

USERS = ["alice_dev", "bob_finance", "charlie_ops", "dave_sales"]

class Simulator:
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.current_time = time.time()
        
    def generate_events(self, step: int) -> List[APIEvent]:
        events = []
        num_events = random.randint(5, 15)
        
        # Normal traffic
        for _ in range(num_events):
            user = random.choice(USERS)
            endpoint = random.choice(["api.internal.com/v1/users", "api.internal.com/v1/data", "aws.amazon.com/s3"])
            bytes_transfer = random.randint(500, 5000)
            events.append(APIEvent(
                timestamp=self.current_time,
                user_id=user,
                endpoint=endpoint,
                bytes_transferred=bytes_transfer,
                is_suspicious=False
            ))
            self.current_time += 1.0

        # Inject Shadow AI usage based on task_id and step
        if self.task_id == "easy":
            # Obvious usage
            if step > 2 and step % 2 == 0:
                events.append(APIEvent(
                    timestamp=self.current_time,
                    user_id="bob_finance",
                    endpoint="api.openai.com/v1/completions",
                    bytes_transferred=120000,
                    is_suspicious=True
                ))
        elif self.task_id == "medium":
            # Subtle usage
            if step > 5 and step % 3 == 0:
                events.append(APIEvent(
                    timestamp=self.current_time,
                    user_id="charlie_ops",
                    endpoint="custom-proxy.shadow.ai/v1",
                    bytes_transferred=15000,
                    is_suspicious=True
                ))
        elif self.task_id == "hard":
            # Exfiltration + Adversarial
            if step > 8:
                # low and slow
                events.append(APIEvent(
                    timestamp=self.current_time,
                    user_id="alice_dev",
                    endpoint="104.18.32.1/telemetry", 
                    bytes_transferred=1000,
                    is_suspicious=True
                ))
                
        return events
