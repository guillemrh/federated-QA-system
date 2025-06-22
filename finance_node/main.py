from fastapi import FastAPI
from .endpoints import router

app = FastAPI(title="Finance Node API")
app.include_router(router)
