from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from src.core.config import settings
from src.api.auth_routes import get_current_user # Assuming get_current_user is in auth_routes.py

router = APIRouter()

templates = Jinja2Templates(directory="src/web/templates")

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Check if user is authenticated, redirect to dashboard if so
    # This is a simplified check, actual authentication check will be more robust
    user = request.session.get("user")
    if user:
        return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
async def read_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "google_client_id": settings.GOOGLE_CLIENT_ID})

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, current_user: dict = Depends(get_current_user)):
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": current_user})
