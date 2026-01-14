from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .router import router

app = FastAPI(title="ASK GEETA AI")

# Include the API router
app.include_router(router)

# Mount static files (Frontend)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
