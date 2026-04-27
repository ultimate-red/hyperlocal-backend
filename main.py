from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes import auth, tasks

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Hyperlocal Platform API",
    description="Phase 0 - Core task loop",
    version="0.1.0"
)

# Configure CORS for Android app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(tasks.router)

@app.get("/")
def root():
    return {
        "message": "Hyperlocal Platform API - Phase 0",
        "version": "0.1.0",
        "status": "running"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
