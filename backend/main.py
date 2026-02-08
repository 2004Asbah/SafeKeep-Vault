from fastapi import FastAPI
from database import Base, engine
from routes.auth_routes import router as auth_router
from routes.file_routes import router as file_router
from routes.audit_routes import router as audit_router

app = FastAPI(title="Safekeep NGO Vault Backend")

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(file_router)
app.include_router(audit_router)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/health/compression")
def compression_health():
    """Check if Ghostscript is available for compression"""
    from compression_engine import verify_ghostscript
    available, message = verify_ghostscript()
    return {
        "ghostscript_available": available,
        "message": message,
        "status": "ready" if available else "fallback_only"
    }

