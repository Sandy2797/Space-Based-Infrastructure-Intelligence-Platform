from app.api.images import router as images_router
from fastapi import FastAPI
from app.api.monitoring_areas import router as monitoring_area_router
from app.api.detections import router as detection_router

app = FastAPI(
    title="Space-Based Infrastructure Intelligence Platform",
    description="Backend API for satellite-based infrastructure monitoring",
    version="0.1.0",
)

app.include_router(detection_router)
app.include_router(images_router)
app.include_router(monitoring_area_router)
@app.get("/")
def home():
    return {
        "project": "Space-Based Infrastructure Intelligence Platform",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "backend",
    }
