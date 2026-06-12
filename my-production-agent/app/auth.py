from fastapi import Header, HTTPException
from .config import settings

def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    if x_api_key != settings.AGENT_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    # Return user_id derived from API key, since we don't have a DB of users
    return "user1"
