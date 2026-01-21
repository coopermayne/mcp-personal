"""FastAPI application for lifelogger."""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from mcp.server.sse import SseServerTransport

from lifelogger.api.routes import entries, cards, stats
from lifelogger.mcp.server import server as mcp_server

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

# Include routers with /api prefix for production
app.include_router(entries.router, prefix="/api")
app.include_router(cards.router, prefix="/api")
app.include_router(stats.router, prefix="/api")


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}


# MCP SSE transport for remote connections
sse_transport = SseServerTransport("/mcp/messages/")


@app.get("/mcp/sse")
async def mcp_sse(request: Request):
    """SSE endpoint for MCP client connections."""
    async with sse_transport.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await mcp_server.run(
            streams[0], streams[1], mcp_server.create_initialization_options()
        )


@app.post("/mcp/messages/")
async def mcp_messages(request: Request):
    """Handle MCP messages from clients."""
    await sse_transport.handle_post_message(
        request.scope, request.receive, request._send
    )


# Serve static frontend if available (production build)
STATIC_DIR = Path(__file__).parent.parent.parent / "static"

if STATIC_DIR.exists():
    # Serve static assets
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    # Catch-all route for SPA - must be after API routes
    @app.get("/{path:path}")
    async def serve_spa(request: Request, path: str):
        """Serve the SPA for any non-API route."""
        # If it's an API or MCP route that wasn't matched, return 404
        if path.startswith("api/") or path.startswith("mcp/"):
            return {"error": "Not found"}
        # Serve index.html for all other routes (SPA handles routing)
        return FileResponse(STATIC_DIR / "index.html")
else:
    # No static files - API only mode
    @app.get("/")
    def root():
        """Health check endpoint."""
        return {"status": "ok", "service": "lifelogger", "mode": "api-only"}
