from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.action.router import router as action_router
from src.authentication.router import router as auth_controller
from src.setting import settings
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI(root_path="/api")

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
app.include_router(auth_controller, prefix="/auth", tags=["auth"])
app.include_router(action_router, prefix="/action", tags=["action"])
