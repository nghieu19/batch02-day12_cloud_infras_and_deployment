import time
import redis
from fastapi import HTTPException
from .config import settings

r = redis.from_url(settings.REDIS_URL, decode_responses=True)

def check_rate_limit(user_id: str):
    now = int(time.time())
    window_start = now - 60
    key = f"rate_limit:{user_id}"
    
    # Remove older requests
    r.zremrangebyscore(key, 0, window_start)
    
    # Count requests in the current window
    request_count = r.zcard(key)
    
    if request_count >= settings.RATE_LIMIT_PER_MINUTE:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Add current request
    r.zadd(key, {str(now): now})
    # Set expiry to 60 seconds to clean up inactive keys
    r.expire(key, 60)
