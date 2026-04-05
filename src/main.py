from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from src.env import ShadowAIEnv
from src.models import Observation, Action, Reward, EnvState

app = FastAPI(title="Shadow AI Detection and Risk Scoring Environment")
env = ShadowAIEnv()

class ResetRequest(BaseModel):
    task_id: str = "easy"

class StepResponse(BaseModel):
    observation: Observation
    reward: Reward
    done: bool
    info: Dict[str, Any]

@app.post("/reset", response_model=Observation)
def reset_env(req: ResetRequest):
    return env.reset(task_id=req.task_id)

@app.post("/step", response_model=StepResponse)
def step_env(action: Action):
    if env.state_data.done:
        raise HTTPException(status_code=400, detail="Episode already done. Please reset.")
    obs, reward, done, info = env.step(action)
    return StepResponse(
        observation=obs,
        reward=reward,
        done=done,
        info=info
    )

@app.get("/state", response_model=EnvState)
def get_state():
    return env.state()
