from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routers import router_health, router_auth, router_admin, router_agents, router_rag, router_borrower
import uvicorn
from pathlib import Path

# Determine frontend path
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"

app = FastAPI(
    title="LOUS API",
    description="AI Automated Loan Origination Underwriting System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers FIRST
app.include_router(router_health.router, prefix="/api", tags=["Health"])
app.include_router(router_auth.router, prefix="/api", tags=["Authentication"])
app.include_router(router_admin.router, prefix="/api", tags=["Admin"])
app.include_router(router_borrower.router, prefix="/api", tags=["Borrower"])
app.include_router(router_rag.router, prefix="/api", tags=["RAG"])
app.include_router(router_agents.router, prefix="/api", tags=["Agents"])

# Mount static files AFTER API routes but BEFORE catch-all
if frontend_dist.exists():
    assets_dir = frontend_dist / "assets"
    if assets_dir.exists():
        # Mount the assets directory for JS/CSS files
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

# Test route to verify Docker is working
@app.get("/test")
async def serve_test():
    """Serve a simple test page"""
    test_file = Path(__file__).parent.parent / "test.html"
    if test_file.exists():
        return FileResponse(test_file, media_type="text/html")
    return {"message": "Test file not found"}

# SPA catch-all route - MUST be defined LAST
@app.get("/{full_path:path}")
async def serve_spa(request: Request, full_path: str):
    """Serve the SPA for all routes that don't match API or static files"""

    # If it starts with 'api/', let it fall through to 404
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")

    # Serve index.html for all other paths (SPA routing)
    index_file = frontend_dist / "index.html"
    if index_file.exists():
        return FileResponse(
            index_file,
            media_type="text/html",
            headers={"Cache-Control": "no-cache"}
        )

    # Fallback if frontend not built
    return {
        "error": "Frontend not built",
        "message": "The frontend has not been built. Run 'npm run build' in the frontend directory.",
        "api_docs": "/docs",
        "frontend_path": str(frontend_dist),
        "exists": frontend_dist.exists()
    }

if __name__ == "__main__":
    print("="*50)
    print(f"Frontend path: {frontend_dist}")
    print(f"Frontend exists: {frontend_dist.exists()}")
    if frontend_dist.exists():
        print(f"Assets exist: {(frontend_dist / 'assets').exists()}")
        print(f"Index.html exists: {(frontend_dist / 'index.html').exists()}")
    print("="*50)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
