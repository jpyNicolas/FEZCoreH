import os.path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from app.api.api_v1 import api
from app.config import settings

if not os.path.exists(settings.local_save_files):
    os.mkdir(settings.local_save_files)

app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=settings.local_save_files), name="static")
app.include_router(api.api_router)
