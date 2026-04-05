# Shadow AI Detection and Risk Scoring Environment

Welcome to the Shadow AI Detection and Risk Scoring Environment, an OpenEnv compatible simulation engine for enterprise cybersecurity.

## Problem Description
"Shadow AI" refers to the unauthorized, unmonitored usage of external artificial intelligence services (like ChatGPT, Claude, etc.) or custom hosted endpoints by employees within an enterprise. This poses significant risks involving data exfiltration, regulatory non-compliance, and intellectual property leaks.

## Environment Motivation
This environment simulates real-world enterprise network traffic, allowing AI agents to evaluate sequences of API logs, assign anomaly and risk scores, and dynamically respond to evolving threats without requiring access to an actual enterprise firewall. 

## Observation and Action Space

### Observation Space
The observation provides context required for detection:
* **current_step**: Current step count in the simulated episode.
* **recent_events**: A list of recently observed network/API transactions.
* **radar_anomaly_score**: Output of the multidimensional radar detection module.
* **historical_risk_score**: Normalized output of the safe decision model tracking long-term risk.
* **user_behavior_summaries**: Profile summaries of baseline behavior for known employees.
* **system_load**: Noise indicator affecting transaction frequency.

### Action Space
* **allow**: Permit the regular traffic.
* **flag**: Mark traffic as highly suspicious (blocks Shadow AI, triggers rewards).
* **monitor**: Increase logging detail without alerting.
* **block**: Actively terminate the connection (blocks Shadow AI, triggers rewards).
* **increase_risk_score**: Manually increment the user's threat level.

The penalty logic ensures false positives (`block` or `flag` on normal users) result in a negative reward.

## Task Descriptions

1. **EASY:** Obvious usage. Direct misuses (e.g. hitting `api.openai.com/v1/completions` from unapproved finance users) with large data payloads.
2. **MEDIUM:** Subtle behavioral anomalies. Traffic disguised as standard API operations, requiring historical tracking to flag intermittent proxy usage over time. 
3. **HARD:** Adversarial evasion. Low-and-slow telemetry exfiltration patterns with small chunk sizes mixed in heavily with noisy standard behaviors.

## Setup Instructions

Ensure Docker is installed.

```bash
# Build the container
docker build -t openenv-shadow-ai .

# Run the container (starts the FastAPI server on port 8000)
docker run -p 8000:8000 openenv-shadow-ai
```

## Deployment Steps
1. Push to an image registry or deploy via Hugging Face Space by choosing a Docker Space and tagging it `openenv`.
2. Validated API endpoints include `/reset`, `/step`, `/state`.

## Baseline Results
The repository includes an `inference.py` script showcasing integration with OpenAI client architectures for evaluating the base difficulty levels.

```bash
# Set your model configuration
export MODEL_NAME="gpt-4-turbo"
export OPENAI_API_KEY="sk-..."

# Run inference against local environment
python inference.py
```
