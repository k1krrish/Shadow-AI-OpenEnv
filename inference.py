import os
import time
import requests
import json
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("API_KEY")

# The Environment API Server URL (FastAPI)
ENV_URL = os.getenv("ENV_URL", "http://localhost:7860")

try:
    client = OpenAI(
        api_key=HF_TOKEN or "dummy_key",
        base_url=API_BASE_URL
    )
except Exception:
    client = None

def run_task(task_id: str):
    # [START] EVENT
    print(f"[START] task={task_id} env=shadow_ai model={MODEL_NAME}")
    
    res = requests.post(f"{ENV_URL}/reset", json={"task_id": task_id})
    if res.status_code != 200:
        return
        
    obs = res.json()
    done = False
    
    system_prompt = """
You are an advanced cybersecurity agent detecting Shadow AI usage. 
Analyze the observations and choose one of the following actions: 'allow', 'flag', 'monitor', 'block', 'increase_risk_score'.
Output exactly a JSON object: {"decision": "...", "reasoning": "..."}. Respond ONLY with the JSON object.
"""
    history = [{"role": "system", "content": system_prompt}]
    
    step_num = 0
    rewards_history = []
    
    while not done:
        step_num += 1
        history.append({"role": "user", "content": f"Observation: {json.dumps(obs)}"})
        
        error_msg = "null"
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
            reasoning = f"Fallback action due to error"
            action_data = {"decision": decision, "reasoning": reasoning}
            error_msg = str(e).replace('\n', ' ')
            
        step_res = requests.post(f"{ENV_URL}/step", json={"decision": decision, "reasoning": reasoning})
        
        if step_res.status_code != 200:
            error_msg = step_res.text.replace('\n', ' ')
            break
            
        step_data = step_res.json()
        obs = step_data["observation"]
        done = step_data["done"]
        reward_val = float(step_data["reward"]["value"])
        rewards_history.append(reward_val)
        
        done_str = "true" if done else "false"
        action_str = json.dumps(action_data).replace(' ', '')
        
        # [STEP] EVENT
        print(f"[STEP] step={step_num} action={action_str} reward={reward_val:.2f} done={done_str} error={error_msg}")
        
        history.append({"role": "assistant", "content": json.dumps(action_data)})
        
    # Grade the task
    state_res = requests.get(f"{ENV_URL}/state")
    final_score = 0.0
    success = False
    
    if state_res.status_code == 200:
        state = state_res.json()
        score = 0.0
        success = state.get('detected_shadow_ai', False)
        
        if success:
            score += 0.5
            
        fp = state.get('false_positives', 0)
        md = state.get('missed_detections', 0)
        score -= (fp * 0.2) + (md * 0.2)
        
        final_score = max(0.0, min(1.0, score + (0.5 if success else 0.0)))
        
    success_str = "true" if success else "false"
    rewards_str = ",".join([f"{r:.2f}" for r in rewards_history])
    if not rewards_str:
        rewards_str = "0.00"
        
    # [END] EVENT
    print(f"[END] success={success_str} steps={step_num} score={final_score:.2f} rewards={rewards_str}")

if __name__ == "__main__":
    ready = False
    for i in range(15):
        try:
            if requests.get(f"{ENV_URL}/state").status_code == 200:
                ready = True
                break
        except:
            time.sleep(1)
            
    if ready:
        run_task("easy")
        run_task("medium")
        run_task("hard")
