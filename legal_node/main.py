from fastapi import FastAPI
from .endpoints import router

app = FastAPI(title="Legal Node API")
app.include_router(router)
