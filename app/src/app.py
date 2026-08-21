from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.access.router import router as access_router
from src.action.router import router as action_router
from src.assignment.router import router as assignment_router
from src.authentication.router import router as auth_controller
from src.handler import register_exception_handlers
from src.object.router import router as object_controller
from src.permission.router import router as permission_controller
from src.role.router import router as role_controller
from src.scope.router import scope_router, scope_type_router
from src.setting import settings
from src.user.router import router as user_controller
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI(root_path="/api")
register_exception_handlers(app)

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
app.include_router(scope_type_router, prefix="/scope_type", tags=["scope"])
app.include_router(object_controller, prefix="/object", tags=["object"])
app.include_router(permission_controller, prefix="/permission", tags=["permission"])
app.include_router(user_controller, prefix="/user", tags=["user"])
app.include_router(role_controller, prefix="/role", tags=["role"])
app.include_router(assignment_router, prefix="/assignment", tags=["assignment"])
app.include_router(access_router, prefix="/access", tags=["access"])
app.include_router(scope_router, prefix="/scope", tags=["scope"])
