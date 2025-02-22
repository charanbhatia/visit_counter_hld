from fastapi import FastAPI, HTTPException
from redis_cache import RedisCache
import redis

app = FastAPI(title="Website Visit Counter")
redis_cache = RedisCache()

@app.post("/visits/{page_id}")
async def increment_visits(page_id: str):
    """
    Increment the visit counter for a specific page
    Counts are batched and flushed periodically to Redis
    """
    try:
        count = redis_cache.increment_count(page_id)
        return {
            "visits": count,
            "served_via": "batch"
        }
    except redis.ConnectionError:
        raise HTTPException(status_code=503, detail="Redis service unavailable")

@app.get("/visits/{page_id}")
async def get_visits(page_id: str):
    """
    Get the current visit count for a specific page
    Forces a buffer flush to ensure accuracy
    """
    try:
        count, source = redis_cache.get_count(page_id)
        return {
            "visits": count,
            "served_via": source
        }
    except redis.ConnectionError:
        raise HTTPException(status_code=503, detail="Redis service unavailable")

@app.get("/health")
async def health_check():
    """Check the health of the API and Redis connection"""
    redis_status = redis_cache.health_check()
    return {
        "api_status": "healthy",
        "redis_status": "healthy" if redis_status else "unhealthy"
    }