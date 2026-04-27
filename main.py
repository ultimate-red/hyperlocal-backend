import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from routes import auth, tasks, users

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Hyperlocal Platform API",
    description="Phase 1 — Google OAuth2 + user profiles",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(users.router)


@app.get("/")
def root():
    return {"message": "Hyperlocal Platform API", "version": "0.2.0", "status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
