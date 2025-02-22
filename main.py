# main.py
from fastapi import FastAPI, HTTPException
from typing import Dict

app = FastAPI(title="Website Visit Counter")

# In-memory storage for visit counts
visit_counts: Dict[str, int] = {}

@app.post("/visits/{page_id}")
async def increment_visits(page_id: str):
    """
    Increment the visit counter for a specific page
    """
    if page_id not in visit_counts:
        visit_counts[page_id] = 0
    visit_counts[page_id] += 1
    return {
        "visits": visit_counts[page_id],
        "served_via": "in_memory"
    }

@app.get("/visits/{page_id}")
async def get_visits(page_id: str):
    """
    Get the current visit count for a specific page
    """
    if page_id not in visit_counts:
        visit_counts[page_id] = 0
    
    return {
        "visits": visit_counts[page_id],
        "served_via": "in_memory"
    }

# For testing purposes
@app.get("/")
async def root():
    """
    Root endpoint to verify API is running
    """
    return {"status": "Website Visit Counter is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)