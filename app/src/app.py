from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.authentification.router import router as auth_controller
from src.setting import settings
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET,
    same_site="lax",
    https_only=settings.MODE != "dev",
    max_age=600,
)
app.include_router(auth_controller)
