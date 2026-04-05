import os
import time
import requests
import json
from openai import OpenAI

LLM_API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4-turbo")
HF_TOKEN = os.getenv("HF_TOKEN", "")

# The Environment API Server URL (FastAPI)
ENV_URL = os.getenv("ENV_URL", "http://localhost:7860")

try:
    client = OpenAI(
        api_key=HF_TOKEN or "dummy_key",
        base_url=LLM_API_BASE_URL
    )
except Exception:
    client = None

def run_task(task_id: str):
    # STRICT OUTPUT FORMAT
    print(f"[START] {task_id}")
    
    res = requests.post(f"{ENV_URL}/reset", json={"task_id": task_id})
    if res.status_code != 200:
        print(f"Failed to reset environment: {res.text}")
        return
        
    obs = res.json()
    done = False
    
    system_prompt = """
You are an advanced cybersecurity agent detecting Shadow AI usage. 
Analyze the observations and choose one of the following actions: 'allow', 'flag', 'monitor', 'block', 'increase_risk_score'.
Output exactly a JSON object: {"decision": "...", "reasoning": "..."}. Respond ONLY with the JSON object.
"""
    history = [{"role": "system", "content": system_prompt}]
    
    while not done:
        # STRICT OUTPUT FORMAT
        print(f"[STEP] {json.dumps(obs)}")
        
        history.append({"role": "user", "content": f"Observation: {json.dumps(obs)}"})
        
        try:
            if not client:
                raise Exception("Missing OpenAI Client")
            
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=history,
                response_format={"type": "json_object"},
                temperature=0.0
            )
            action_json = response.choices[0].message.content
            
            action_data = json.loads(action_json)
            decision = action_data.get("decision", "monitor")
            reasoning = action_data.get("reasoning", "")
        except Exception as e:
            decision = "monitor"
            reasoning = f"Fallback action due to error: {e}"
            action_data = {"decision": decision, "reasoning": reasoning}
            
        step_res = requests.post(f"{ENV_URL}/step", json={"decision": decision, "reasoning": reasoning})
        
        if step_res.status_code != 200:
            print(f"Error executing step: {step_res.text}")
            break
            
        step_data = step_res.json()
        obs = step_data["observation"]
        done = step_data["done"]
        
        history.append({"role": "assistant", "content": json.dumps(action_data)})
        
    # Grade the task
    state_res = requests.get(f"{ENV_URL}/state")
    final_score = 0.0
    if state_res.status_code == 200:
        state = state_res.json()
        score = 0.0
        if state.get('detected_shadow_ai', False):
            score += 0.5
        fp = state.get('false_positives', 0)
        md = state.get('missed_detections', 0)
        score -= (fp * 0.2) + (md * 0.2)
        
        final_score = max(0.0, min(1.0, score + (0.5 if state.get('detected_shadow_ai', False) else 0.0)))
        
    # STRICT OUTPUT FORMAT
    print(f"[END] {final_score}")

if __name__ == "__main__":
    ready = False
    for i in range(15):
        try:
            if requests.get(f"{ENV_URL}/state").status_code == 200:
                ready = True
                break
        except:
            time.sleep(1)
            
    if not ready:
        print("API not reachable.")
    else:
        run_task("easy")
        run_task("medium")
        run_task("hard")
