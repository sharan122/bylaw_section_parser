from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import extract, translate

app = FastAPI(title="Bylaw Parser API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(extract.router, prefix="/api", tags=["extract"])
app.include_router(translate.router, prefix="/api", tags=["translate"])


@app.get("/")
async def root():
    return {"message": "Bylaw Parser API", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}

