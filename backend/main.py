# ------------------------------------------------------------------------
# FastAPI Orchestrator
# ------------------------------------------------------------------------

from fastapi import FastAPI
from app.routers import story_api


version = "0.0.1"

app = FastAPI(
    title="GenVN Engine",
    description="Backend orchestrator for GenVN application.",
    version=version
)

# --------------------------- Include Routers ---------------------------

app.include_router(
    story_api.router, 
    prefix=f"/api/story", 
    tags=["story"]
)

# TODO: asset router if I add a asset upload/edit feature

# --------------------------- Health Check ---------------------------
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "version": version
    }

# --------------------------- Run App ---------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)