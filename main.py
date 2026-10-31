import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.database import init_db
from backend.routers import auth, problems, concepts, stats, revision, data_transfer

# Initialize database
init_db()

app = FastAPI(title="Minimal DSA Tracker", version="1.0.0")

# Include API routers
app.include_router(auth.router)
app.include_router(problems.router)
app.include_router(concepts.router)
app.include_router(revision.router)
app.include_router(stats.router)
app.include_router(data_transfer.router)

# Base directory for static files
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

# HTML Page Routes (Multi-page website)
@app.get("/")
@app.get("/dashboard")
def page_dashboard():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/concepts")
def page_concepts():
    return FileResponse(os.path.join(STATIC_DIR, "concepts.html"))

@app.get("/problems")
def page_problems():
    return FileResponse(os.path.join(STATIC_DIR, "problems.html"))

@app.get("/revision")
def page_revision():
    return FileResponse(os.path.join(STATIC_DIR, "revision.html"))

@app.get("/profile")
def page_profile():
    return FileResponse(os.path.join(STATIC_DIR, "profile.html"))

@app.get("/login")
def page_login():
    return FileResponse(os.path.join(STATIC_DIR, "login.html"))

# Mount static assets (CSS, JS, images)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
