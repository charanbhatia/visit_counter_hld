from fastapi import FastAPI, HTTPException
from redis_cache import RedisCache

app = FastAPI(title="Website Visit Counter")
redis_cache = RedisCache()

@app.post("/visits/{page_id}")
async def increment_visits(page_id: str):
    """
    Increment the visit counter for a specific page
    Counts are batched and stored in the appropriate shard
    """
    try:
        count, shard_id = redis_cache.increment_count(page_id)
        return {
            "visits": count,
            "served_via": shard_id
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.get("/visits/{page_id}")
async def get_visits(page_id: str):
    """
    Get the current visit count for a specific page
    Retrieves from the appropriate shard
    """
    try:
        count, source = redis_cache.get_count(page_id)
        return {
            "visits": count,
            "served_via": source
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.get("/health")
async def health_check():
    """Check the health of all Redis shards"""
    status = redis_cache.health_check()
    return {
        "api_status": "healthy",
        "redis_status": status
    }