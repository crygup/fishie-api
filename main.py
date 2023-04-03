from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.security import APIKeyHeader

from config import apikey
from utils import ytdl

X_API_KEY = APIKeyHeader(name="X-API-Key")


def api_key_auth(x_api_key: str = Depends(X_API_KEY)):
    if x_api_key != apikey:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key. Check that you are passing a 'X-API-Key' on your header.",
        )


root = FastAPI(dependencies=[Depends(api_key_auth)])
app = APIRouter(prefix="/api")
root.include_router(app)
app.include_router(ytdl)
