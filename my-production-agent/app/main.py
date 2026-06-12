import time
import signal
import json
import logging
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Request

from .config import settings
from .auth import verify_api_key
from .rate_limiter import check_rate_limit
from .cost_guard import check_budget, record_cost
import redis

# Structured JSON logging setup
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

def log_event(event: str, **kwargs):
    logger.info(json.dumps({"event": event, **kwargs}))

app = FastAPI()
r = redis.from_url(settings.REDIS_URL, decode_responses=True)

# Graceful shutdown handler
def shutdown_handler(signum, frame):
    log_event("shutdown", signum=signum)
    # Perform cleanup if necessary
    
signal.signal(signal.SIGTERM, shutdown_handler)

@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0"}

@app.get("/ready")
def ready():
    try:
        r.ping()
        return {"status": "ready"}
    except Exception as e:
        log_event("ready_fail", error=str(e))
        raise HTTPException(status_code=503, detail="Not ready")

@app.post("/ask")
def ask(
    request: Request,
    body: dict,
    user_id: str = Depends(verify_api_key)
):
    # body should have "question", maybe "user_id" from the client side but we use the one from verify_api_key
    question = body.get("question", "")
    if not question:
        raise HTTPException(status_code=400, detail="Missing question")
        
    check_rate_limit(user_id)
    
    # Simple input tokens cost estimate
    input_tokens = len(question.split())
    estimated_input_cost = input_tokens * 0.0001
    check_budget(user_id, estimated_input_cost)
    
    # Store history to Redis for stateless design
    history_key = f"history:{user_id}"
    r.rpush(history_key, f"Q: {question}")
    
    # Mock LLM logic
    answer = f"Mock answer to: {question}"
    output_tokens = len(answer.split())
    estimated_output_cost = output_tokens * 0.0002
    
    record_cost(user_id, estimated_input_cost + estimated_output_cost)
    r.rpush(history_key, f"A: {answer}")
    
    log_event("ask_processed", user_id=user_id, question_length=len(question))
    
    return {
        "question": question,
        "answer": answer,
        "user_id": user_id
    }
