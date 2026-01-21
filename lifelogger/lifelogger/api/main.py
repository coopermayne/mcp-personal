"""FastAPI application for lifelogger."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from lifelogger.api.routes import entries, cards, stats

app = FastAPI(
    title="Lifelogger",
    description="Personal knowledge system with spaced repetition",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(entries.router)
app.include_router(cards.router)
app.include_router(stats.router)


@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "lifelogger"}


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}
