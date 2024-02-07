# uvicorn app

# Path: sqlcoder/serve.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlcoder import __version__
import sqlcoder.integration_routes, sqlcoder.query_routes

app = FastAPI()

app.include_router(sqlcoder.integration_routes.router)
app.include_router(sqlcoder.query_routes.router)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"SQLCoder": __version__}

@app.get("/health")
def health_check():
    return {"status": "ok"}
