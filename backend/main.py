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
